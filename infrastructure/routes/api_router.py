from fastapi import APIRouter

from app.api.v1.controller import (file_controller, training_controller, program_controller, pilgrim_controller,
                                   view_field_controller, customer_controller, food_menu_controller, route_controller,
                                   ziara_controller, script_controller, admin_user_controller, payment_controller,
                                   add_ons_service_controller, package_assign_controller, search_controller)
from app.api.v1.controller import (user_controller, package_controller, admin_controller)
from app.api.v1.controller.admin_user_controller import public_router

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

router.include_router(food_menu_controller.private_router)
router.include_router(route_controller.private_router)
router.include_router(ziara_controller.ziara_router)
router.include_router(script_controller.private_router)

router.include_router(admin_user_controller.private_router)

router.include_router(admin_user_controller.public_router)
router.include_router(payment_controller.private_router)

router.include_router(add_ons_service_controller.private_router)
router.include_router(package_assign_controller.private_router)

router.include_router(search_controller.private_router)