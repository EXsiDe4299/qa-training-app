from fastapi import APIRouter, HTTPException

from qa_training_app.db import get_db
from qa_training_app.users.repository import UserRepository
from qa_training_app.users.schemas import RegisterRequest, UserResponse
from qa_training_app.users.service import UserAlreadyExistsError, UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/register", status_code=201, response_model=UserResponse)
def register(data: RegisterRequest):
    with get_db() as conn:
        repository = UserRepository(conn)
        service = UserService(repository)

        try:
            user = service.register(
                username=data.username,
                password=data.password,
            )
        except UserAlreadyExistsError:
            raise HTTPException(
                status_code=409,
                detail="Username already exists",
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            )

    return UserResponse(id=user.id, username=user.username)
