from fastapi import APIRouter

from app.api.v1.controller import ( problem_category_controller )

router = APIRouter()

# routers
# router.include_router(problem_category_controller.router)

