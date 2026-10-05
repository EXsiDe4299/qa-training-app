from fastapi import APIRouter

from qa_training_app.auth.router import router as auth_router
from qa_training_app.requests.router import router as requests_router
from qa_training_app.users.router import router as users_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(requests_router)
