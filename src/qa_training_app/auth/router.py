from fastapi import APIRouter, Depends, HTTPException, Request

from qa_training_app.auth.deps import get_current_user_id
from qa_training_app.auth.schemas import (
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
)
from qa_training_app.auth.service import AuthService
from qa_training_app.db import get_db
from qa_training_app.users.repository import UserRepository

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, request: Request):
    with get_db() as conn:
        repository = UserRepository(conn)
        service = AuthService(repository)
        user_id = service.login(
            username=data.username,
            password=data.password,
        )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    request.session["user_id"] = user_id

    return LoginResponse(
        user_id=user_id,
        username=data.username.strip(),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request):
    request.session.clear()
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=AuthUserResponse)
def me(
    request: Request,
    user_id: int = Depends(get_current_user_id),
):
    with get_db() as conn:
        repository = UserRepository(conn)
        user = repository.get_by_id(user_id)

    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    return AuthUserResponse(
        id=user.id,
        username=user.username,
    )
