from .auth_router import router as auth_router
from .deposits_router import router as deposits_router
from .proposals_router import router as proposals_router
from .purchases_router import router as purchases_router

__all__ = [
    "auth_router",
    "deposits_router",
    "proposals_router",
    "purchases_router"
]
