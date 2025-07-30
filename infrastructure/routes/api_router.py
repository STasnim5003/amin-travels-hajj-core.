from fastapi import APIRouter

from app.api.v1.controller import (user_controller)

router = APIRouter()

# routers
router.include_router(user_controller.router)


