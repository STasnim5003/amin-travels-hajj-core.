from fastapi import APIRouter

from app.api.v1.controller import (file_controller, training_controller)
from app.api.v1.controller import (user_controller, package_controller, admin_controller)

router = APIRouter()

# routers
router.include_router(user_controller.router)
router.include_router(user_controller.private_router)
router.include_router(package_controller.router)
router.include_router(file_controller.router)

router.include_router(admin_controller.router)

router.include_router(training_controller.router)

