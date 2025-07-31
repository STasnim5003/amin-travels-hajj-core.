from fastapi import APIRouter

from app.api.v1.controller import (user_controller, package_controller)

router = APIRouter()

# routers
router.include_router(user_controller.router)
router.include_router(package_controller.router)


