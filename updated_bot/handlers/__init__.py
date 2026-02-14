from .master_admin_handlers import router as master_admin_router
from .admin_handlers import router as admin_router
from .customer_handlers import router as customer_router
from .shop_settings import router as settings_router
from .payment_handlers import router as payment_router
from .migration_handlers import router as migration_router

__all__ = [
    "master_admin_router",
    "admin_router",
    "customer_router",
    "settings_router",
    "payment_router",
    "migration_router"
]
