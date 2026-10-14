import random
import string
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import package_assign_repository, pilgrim_repository, add_ons_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignUpdateSchema, \
    PackageAssignForMultiplePilgrimSchema, PackageAssignUpdateItemSchema, PackageUnassignSchema
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
    discounts = request.discounts or {}
    unknown = set(discounts) - set(request.tracking_ids)
    if unknown:
        raise HTTPException(status_code=400, detail=f"Discount given for pilgrims not selected: {', '.join(sorted(unknown))}")

    shared = request.model_dump(exclude={"tracking_ids", "total_payable", "discounts", "package_price_discount"})
    changes = [
        PackageAssignUpdateItemSchema(
            tracking_id=tracking_id,
            package_price_discount=discounts.get(tracking_id, request.package_price_discount),
            **shared,
        )
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


async def unassign_package(db: AsyncSession, request: PackageUnassignSchema, agency_name: str, username: str):
    """
    Remove the package from the pilgrims: clear the package fields, delete the package bill rows from the
    ledger and recompute the totals from the remaining payables. Payments are never touched; money already
    paid stays in total_payment and shows up as available amount. All or nothing.
    """
    try:
        tracking_ids = request.tracking_ids
        if not tracking_ids:
            raise HTTPException(status_code=400, detail="No pilgrims given")
        if len(set(tracking_ids)) != len(tracking_ids):
            raise HTTPException(status_code=400, detail="Duplicate tracking IDs")

        pilgrims = {p.tracking_id: p for p in
                    await pilgrim_repository.get_pilgrims_by_tracking_ids(db, tracking_ids, for_update=True)}
        for tracking_id in tracking_ids:
            pilgrim = pilgrims.get(tracking_id)
            if not pilgrim:
                raise HTTPException(status_code=400, detail=f"Pilgrim {tracking_id} not found")
            if pilgrim.group_name != agency_name:
                raise HTTPException(status_code=403, detail=f"Pilgrim {tracking_id} is not in your agency")
            if not pilgrim.is_package_assigned:
                raise HTTPException(status_code=400, detail=f"Pilgrim {tracking_id} has no package assigned")
            if is_closed_season(pilgrim.hajj_year):
                raise HTTPException(status_code=400,
                                    detail=f"Hajj {pilgrim.hajj_year} is closed; billing of pilgrim {tracking_id} can't be changed")

        ledger = await package_assign_repository.get_payable_summary(db, tracking_ids)
        now = get_current_time()
        for tracking_id in tracking_ids:
            total_payable = ledger[tracking_id]["other"]
            total_payment = pilgrims[tracking_id].total_payment or 0
            await package_assign_repository.individual_pilgrim_package_change(db, {
                "tracking_id": tracking_id,
                "package_name": None,
                "package_duration": None,
                "package_bed_types": None,
                "add_ons_services": null(),  # SQL NULL; a plain None would store JSON 'null'
                "package_id": None,
                "package_price_discount": 0,
                "is_package_assigned": False,
                "total_payable": total_payable,
                "actual_payable": total_payable,
                "total_due": max(0, total_payable - total_payment),
                "total_available_amount": max(0, total_payment - total_payable),
                "updated_by": username,
                "updated_at": now,
            })

        await package_assign_repository.replace_package_bills(db, tracking_ids, [])
        await db.commit()
        return {"message": "Package unassigned successfully", "unassigned": tracking_ids}

    except Exception as e:
        await db.rollback()
        raise e


def _to_int(value, label: str) -> int:
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"{label} must be a number")


def _key(name) -> str:
    return " ".join(str(name).split()).lower()


def _price_add_ons(requested: dict | None, catalog: dict) -> dict:
    # Add-on prices always come from the current catalog, so every pilgrim pays the same for the same add-on.
    priced = {}
    for name in requested or {}:
        source = catalog.get(_key(name))
        if not source:
            raise HTTPException(status_code=400, detail=f"Add-on '{name}' not found")
        priced[_key(name)] = (source[0], _to_int(source[1], f"Add-on '{name}' price"))
    return {name: price for name, price in priced.values()}


def is_closed_season(hajj_year) -> bool:
    # A hajj season is closed from August of its year (Hajj is over by then); its bills are final.
    if not hajj_year:
        return False
    today = get_current_time()
    return int(hajj_year) < today.year or (int(hajj_year) == today.year and today.month >= 8)


def current_open_year() -> int:
    today = get_current_time()
    return today.year + 1 if today.month >= 8 else today.year


def _bed_price(package, bed_type: str) -> tuple[str, int]:
    beds = package.bed_type if isinstance(package.bed_type, dict) else {}
    for name, price in beds.items():
        if _key(name) == _key(bed_type):
            return name, _to_int(price, "Bed price")
    raise HTTPException(status_code=400, detail=f"Bed type '{bed_type}' not found in package {package.name}")


async def reprice_assigned_pilgrims(db: AsyncSession, agency_name: str, username: str, *,
                                    package_name: str | None = None, old_duration: int | None = None,
                                    new_duration: int | None = None, package_year: int | None = None,
                                    add_on_old_name: str | None = None,
                                    add_on_new_name: str | None = None,
                                    add_on_year: int | None = None) -> list[str]:
    """
    Re-bill every assigned pilgrim affected by a package or add-on catalog edit, with the caller's
    uncommitted catalog change in the same transaction (this commits). Discounts are kept.
    Pilgrims of closed seasons are never touched; a package edit only reaches pilgrims of that package's year.
    Pilgrims that can no longer be priced (bed type / add-on removed) are left as they are and returned.
    """
    pilgrims = await package_assign_repository.get_package_assigned_pilgrims(db, agency_name)
    old_key = _key(add_on_old_name) if add_on_old_name else None
    changes = []
    for pilgrim in pilgrims:
        if is_closed_season(pilgrim.hajj_year):
            continue
        if package_year and pilgrim.hajj_year and pilgrim.hajj_year != package_year:
            continue
        if add_on_year and (pilgrim.hajj_year or current_open_year()) != add_on_year:
            continue
        if package_name and (pilgrim.package_name, pilgrim.package_duration) != (package_name, old_duration):
            continue
        if old_key and old_key not in {_key(k) for k in (pilgrim.add_ons_services or {})}:
            continue
        add_ons = None
        if old_key and add_on_new_name:
            add_ons = {(add_on_new_name if _key(k) == old_key else k): 0 for k in pilgrim.add_ons_services}
        changes.append(PackageAssignUpdateItemSchema(
            tracking_id=pilgrim.tracking_id, package_duration=new_duration, add_ons_services=add_ons))

    if not changes:
        await db.commit()
        return []
    return await _apply_package_changes(db, changes, agency_name, username, skip_unpriceable=True)


async def _apply_package_changes(db: AsyncSession, changes: list[PackageAssignUpdateItemSchema], agency_name: str,
                                 username: str, fresh: bool = False, require_assigned: bool = False,
                                 skip_unpriceable: bool = False) -> list[str]:
    """
    Single place that prices a package and writes the pilgrim's finance + ledger, all in one transaction.

    Prices are universal: bed price from the current package + add-on prices from the current catalog.
    Only the discount is per pilgrim.
    total_payable  = package price (bed + add-ons) + other payables on the ledger
    actual_payable = total_payable - discount
    The package bill row on the ledger = package price - discount (exactly one per pilgrim).

    fresh=True (assign): discount defaults to 0 instead of the pilgrim's current one.
    skip_unpriceable=True: pilgrims that cannot be priced are skipped (returned) instead of failing the batch.
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
            if pilgrim.is_package_assigned and is_closed_season(pilgrim.hajj_year):
                raise HTTPException(status_code=400,
                                    detail=f"Hajj {pilgrim.hajj_year} is closed; billing of pilgrim {tracking_id} can't be changed")

        # Add-on prices are per Hajj year: each pilgrim is priced from the catalog of their own year.
        catalogs = {}
        for year in {p.hajj_year or current_open_year() for p in pilgrims.values()}:
            if not is_closed_season(year):
                await add_ons_repository.ensure_year_catalog(db, agency_name, year)
            catalogs[year] = {
                _key(a.name): (" ".join(a.name.split()), a.price)
                for a in await add_ons_repository.get_all_add_on_services(db, agency_name, year)
                if a.is_active
            }
        ledger = await package_assign_repository.get_payable_summary(db, tracking_ids)
        packages = {}
        now = get_current_time()
        package_bill_rows = []
        priced_ids, skipped = [], []

        for change in changes:
            pilgrim = pilgrims[change.tracking_id]
            try:
                package_name = change.package_name or pilgrim.package_name
                duration = change.package_duration or pilgrim.package_duration
                bed_type = change.package_bed_types or pilgrim.package_bed_types
                if not (package_name and duration and bed_type):
                    raise HTTPException(status_code=400, detail=f"Package, duration and bed type are required for {pilgrim.tracking_id}")

                requested_add_ons = change.add_ons_services if change.add_ons_services is not None else pilgrim.add_ons_services
                add_ons = _price_add_ons(requested_add_ons, catalogs[pilgrim.hajj_year or current_open_year()])

                cache_key = (package_name, duration, pilgrim.hajj_year)
                if cache_key not in packages:
                    packages[cache_key] = await package_assign_repository.get_hajj_package(
                        db, package_name, duration, agency_name, pilgrim.hajj_year)
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
            except HTTPException:
                if not skip_unpriceable:
                    raise
                skipped.append(pilgrim.tracking_id)
                continue

            summary = ledger[pilgrim.tracking_id]
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

            priced_ids.append(pilgrim.tracking_id)
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

        if priced_ids:
            await package_assign_repository.replace_package_bills(db, priced_ids, package_bill_rows)
        await db.commit()
        return skipped

    except Exception as e:
        await db.rollback()
        raise e
