import fastapi
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.service import training_user_service
from data.db.db_config import get_async_db
from infrastructure.schema.training_schema import TrainingUserResponseSchema, TrainingUserBaseSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@router.post("/training-user", response_model=TrainingUserResponseSchema, tags=["training-users"])
async def create_user_endpoint(
    training_user: TrainingUserBaseSchema,
    db: AsyncSession = Depends(get_async_db)
):
    response = await training_user_service.create_training_user(training_user_request_schema=training_user, db=db)
    return JSONResponse(content=jsonable_encoder(response))
