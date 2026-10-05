from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUserResponse(BaseModel):
    id: int
    username: str


class LoginResponse(BaseModel):
    user_id: int
    username: str


class MessageResponse(BaseModel):
    message: str
