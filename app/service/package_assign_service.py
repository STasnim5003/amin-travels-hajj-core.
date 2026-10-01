import random
import string
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import package_assign_repository, pilgrim_repository, add_ons_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignUpdateSchema, \
    PackageAssignForMultiplePilgrimSchema, PackageAssignUpdateItemSchema
from infrastructure.schema.pilgrim_data_schema import PilgrimDataResponseSchema


async def get_all_package_names(db: AsyncSession, agency_name: str):
    return await package_assign_repository.get_all_package_names(db, agency_name)


async def get_durations_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    return await package_assign_repository.get_durations_by_package_name(db, package_name, agency_name)


async def get_bed_types_by_package_name(db: AsyncSession, package_name: str, duration: int, agency_name: str):
    return await package_assign_repository.get_bed_types_by_package_name(db, package_name, duration, agency_name)


async def get_package_assigned_pilgrims(db: AsyncSession, agency_name: str):
    try:
        result = await package_assign_repository.get_package_assigned_pilgrims(db, agency_name)
        return [PilgrimDataResponseSchema.model_validate(r) for r in result]
    except Exception as e:
        raise e


async def assign_package_for_multiple_pilgrims(db: AsyncSession, request: PackageAssignForMultiplePilgrimSchema,
                                               agency_name: str, username: str):
    changes = [
        PackageAssignUpdateItemSchema(tracking_id=tracking_id, **request.model_dump(exclude={"tracking_ids", "total_payable"}))
        for tracking_id in request.tracking_ids
    ]
    await _apply_package_changes(db, changes, agency_name, username, fresh=True)
    return {"message": "Package assigned and billing updated successfully"}


async def change_assigned_package(db: AsyncSession, request: PackageAssignSchema, agency_name: str, username: str):
    change = PackageAssignUpdateItemSchema(**request.model_dump(exclude={"total_payable"}))
    await _apply_package_changes(db, [change], agency_name, username)
    return {"message": "package changed successfully"}


async def update_assigned_package(db: AsyncSession, request: PackageAssignUpdateSchema, agency_name: str, username: str):
    if request.items:
        changes = request.items
    elif request.tracking_id:
        changes = [PackageAssignUpdateItemSchema(**request.model_dump(exclude={"items", "total_payable"}))]
    else:
        raise HTTPException(status_code=400, detail="tracking_id or items is required")

    await _apply_package_changes(db, changes, agency_name, username, require_assigned=True)
    return {"message": "package updated successfully"}


def _to_int(value, label: str) -> int:
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"{label} must be a number")


def _key(name) -> str:
    return " ".join(str(name).split()).lower()


def _price_add_ons(requested: dict | None, kept: dict | None, catalog: dict) -> dict:
    # Add-ons the pilgrim already has keep their billed price; newly added ones take the catalog price.
    kept_by_key = {_key(name): (name, price) for name, price in (kept or {}).items()}
    priced = {}
    for name in requested or {}:
        key = _key(name)
        source = kept_by_key.get(key) or catalog.get(key)
        if not source:
            raise HTTPException(status_code=400, detail=f"Add-on '{name}' not found")
        priced[key] = (source[0], _to_int(source[1], f"Add-on '{name}' price"))
    return {name: price for name, price in priced.values()}


def _bed_price(package, bed_type: str) -> tuple[str, int]:
    beds = package.bed_type if isinstance(package.bed_type, dict) else {}
    for name, price in beds.items():
        if _key(name) == _key(bed_type):
            return name, _to_int(price, "Bed price")
    raise HTTPException(status_code=400, detail=f"Bed type '{bed_type}' not found in package {package.name}")


async def _apply_package_changes(db: AsyncSession, changes: list[PackageAssignUpdateItemSchema], agency_name: str,
                                 username: str, fresh: bool = False, require_assigned: bool = False):
    """
    Single place that prices a package and writes the pilgrim's finance + ledger, all in one transaction.

    total_payable  = package price (bed + add-ons) + other payables on the ledger
    actual_payable = total_payable - discount
    The package bill row on the ledger = package price - discount (exactly one per pilgrim).

    fresh=True (assign): price everything from the current package/catalog.
    Otherwise an unchanged package/bed keeps its billed base price, so later package price edits never
    silently re-bill a pilgrim; a changed package/bed is priced from the current package.
    """
    try:
        tracking_ids = [c.tracking_id for c in changes]
        if not tracking_ids:
            raise HTTPException(status_code=400, detail="No pilgrims given")
        if len(set(tracking_ids)) != len(tracking_ids):
            raise HTTPException(status_code=400, detail="Duplicate tracking IDs")

        pilgrims = {p.tracking_id: p for p in await pilgrim_repository.get_pilgrims_by_tracking_ids(db, tracking_ids)}
        for tracking_id in tracking_ids:
            pilgrim = pilgrims.get(tracking_id)
            if not pilgrim:
                raise HTTPException(status_code=400, detail=f"Pilgrim {tracking_id} not found")
            if pilgrim.group_name != agency_name:
                raise HTTPException(status_code=403, detail=f"Pilgrim {tracking_id} is not in your agency")
            if require_assigned and not pilgrim.is_package_assigned:
                raise HTTPException(status_code=400, detail=f"Pilgrim {tracking_id} has no package assigned")

        catalog = {
            _key(a.name): (" ".join(a.name.split()), a.price)
            for a in await add_ons_repository.get_all_add_on_services(db, agency_name)
            if a.is_active
        }
        ledger = await package_assign_repository.get_payable_summary(db, tracking_ids)
        packages = {}
        now = get_current_time()
        package_bill_rows = []

        for change in changes:
            pilgrim = pilgrims[change.tracking_id]
            package_name = change.package_name or pilgrim.package_name
            duration = change.package_duration or pilgrim.package_duration
            bed_type = change.package_bed_types or pilgrim.package_bed_types
            if not (package_name and duration and bed_type):
                raise HTTPException(status_code=400, detail=f"Package, duration and bed type are required for {pilgrim.tracking_id}")

            requested_add_ons = change.add_ons_services if change.add_ons_services is not None else pilgrim.add_ons_services
            kept_add_ons = None if fresh else pilgrim.add_ons_services
            add_ons = _price_add_ons(requested_add_ons, kept_add_ons, catalog)

            same_package = (
                not fresh and pilgrim.is_package_assigned
                and (package_name, duration, _key(bed_type))
                == (pilgrim.package_name, pilgrim.package_duration, _key(pilgrim.package_bed_types or ""))
            )
            summary = ledger[pilgrim.tracking_id]
            if same_package:
                bed_type = pilgrim.package_bed_types
                last_bill = summary["last_package_amount"]
                billed_gross = (
                    last_bill + (pilgrim.package_price_discount or 0) if last_bill is not None
                    else (pilgrim.total_payable or 0) - summary["other"]
                )
                old_add_ons = sum(_to_int(v, "Add-on price") for v in (pilgrim.add_ons_services or {}).values())
                base_price = billed_gross - old_add_ons
                if base_price < 0:
                    raise HTTPException(status_code=400, detail=f"Existing bill of {pilgrim.tracking_id} is inconsistent")
            else:
                cache_key = (package_name, duration)
                if cache_key not in packages:
                    packages[cache_key] = await package_assign_repository.get_hajj_package(db, package_name, duration, agency_name)
                package = packages[cache_key]
                if not package:
                    raise HTTPException(status_code=400, detail=f"Package {package_name} ({duration} days) not found")
                bed_type, base_price = _bed_price(package, bed_type)

            package_price = base_price + sum(add_ons.values())
            if change.package_price_discount is not None:
                discount = change.package_price_discount
            else:
                discount = 0 if fresh else (pilgrim.package_price_discount or 0)
            if discount < 0 or discount > package_price:
                raise HTTPException(status_code=400, detail=f"Discount must be between 0 and {package_price}")

            total_payable = package_price + summary["other"]
            actual_payable = total_payable - discount
            total_payment = pilgrim.total_payment or 0

            await package_assign_repository.individual_pilgrim_package_change(db, {
                "tracking_id": pilgrim.tracking_id,
                "package_name": package_name,
                "package_duration": duration,
                "package_bed_types": bed_type,
                "add_ons_services": add_ons,
                "package_price_discount": discount,
                "is_package_assigned": True,
                "total_payable": total_payable,
                "actual_payable": actual_payable,
                "total_due": max(0, actual_payable - total_payment),
                "total_available_amount": max(0, total_payment - actual_payable),
                "updated_by": username,
                "updated_at": now,
            })

            package_bill_rows.append({
                "description": "Package Bill" if fresh else "Updated Package Bill",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "amount": package_price - discount,
                "tracking_id": pilgrim.tracking_id,
                "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "created_by": username,
                "updated_by": username,
                "agency_name": agency_name,
                "category": "Payable",
            })

        await package_assign_repository.replace_package_bills(db, tracking_ids, package_bill_rows)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise e
