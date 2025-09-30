from fastapi import APIRouter

from app.api.v1.controller import (file_controller, training_controller, program_controller, pilgrim_controller,
                                   view_field_controller, customer_controller)
from app.api.v1.controller import (user_controller, package_controller, admin_controller)
from app.api.v1.controller.pilgrim_controller import private_router

router = APIRouter()

# routers
router.include_router(user_controller.router)
router.include_router(user_controller.private_router)
router.include_router(package_controller.router)
router.include_router(package_controller.private_router)
router.include_router(file_controller.router)

router.include_router(admin_controller.router)

router.include_router(training_controller.router)

router.include_router(file_controller.private_router)
router.include_router(program_controller.router)
router.include_router(program_controller.private_router)
router.include_router(pilgrim_controller.private_router)
router.include_router(pilgrim_controller.public_router)
router.include_router(admin_controller.private_router)

router.include_router(view_field_controller.private_router)

router.include_router(customer_controller.private_router)