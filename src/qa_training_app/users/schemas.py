from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class User:
    id: int
    username: str
    password_hash: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
