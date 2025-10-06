from fastapi import HTTPException
from sqlalchemy import insert, select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.view_field_model import ViewFieldModel
from infrastructure.schema.view_field_schema import ViewFieldSchema, ViewFieldResponseSchema

async def create_view(db: AsyncSession, request_body: ViewFieldSchema, username: str) -> ViewFieldResponseSchema:
    request_data = request_body.model_dump(exclude_unset=True, exclude_none=True)
    request_data.update({
        "username": username,
        "created_by": username,
        "updated_by": username
    })

    try:
        stmt = select(ViewFieldModel).where(
            ViewFieldModel.view_name == request_data.get("view_name")
        )
        result = await db.execute(stmt)
        existing_view = result.scalar_one_or_none()

        if existing_view:
            update_stmt = (
                update(ViewFieldModel)
                .where(ViewFieldModel.id == existing_view.id)
                .values(**request_data)
                .returning(ViewFieldModel)
            )
            result = await db.execute(update_stmt)
            updated_view = result.scalar_one()
            await db.commit()
            return ViewFieldResponseSchema.model_validate(updated_view.__dict__)

        else:
            insert_stmt = insert(ViewFieldModel).values(**request_data).returning(ViewFieldModel)
            result = await db.execute(insert_stmt)
            new_view = result.scalar_one_or_none()
            if new_view is None:
                raise HTTPException(status_code=400, detail="Error creating view")
            await db.commit()
            return ViewFieldResponseSchema.model_validate(new_view.__dict__)

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def get_views(db: AsyncSession, username: str) -> list[ViewFieldResponseSchema]:
    try:
        query = (
            select(ViewFieldModel)
            .where(
                and_(
                    ViewFieldModel.username == username
                )
            )
        )
        result = await db.execute(query)
        views = result.scalars().all()

        if not views:
            return []

        return [ViewFieldResponseSchema.model_validate(view, from_attributes=True) for view in views]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

