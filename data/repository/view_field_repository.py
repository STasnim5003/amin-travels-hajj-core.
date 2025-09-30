from fastapi import HTTPException
from sqlalchemy import insert, select, and_
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
        query = insert(ViewFieldModel).values(**request_data).returning(ViewFieldModel)

        result = await db.execute(query)
        new_view: ViewFieldModel = result.scalar_one_or_none()  # fetch the inserted row

        if new_view is None:
            raise HTTPException(status_code=400, detail="Error occurred while creating view")

        await db.commit()
        # Convert SQLAlchemy model to response schema
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

