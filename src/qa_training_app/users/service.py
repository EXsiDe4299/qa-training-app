import re

import bcrypt

from qa_training_app.users.interfaces import UserRepositoryABC
from qa_training_app.users.schemas import User


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, repository: UserRepositoryABC):
        self.repository = repository

    def register(
        self,
        username: str,
        password: str,
    ) -> User:
        username = username.strip()

        if not re.fullmatch(r"[A-Za-z0-9_]*", username):
            raise ValueError(
                "Username must contain only Latin letters, digits, and underscores."
            )

        if not re.fullmatch(r"^[A-Za-z0-9!@#$%^&*_]*$", password):
            raise ValueError(
                "Password must contain only Latin letters, digits, and special characters."
            )

        if len(username) < 3:
            raise ValueError("Username must contain at least 3 characters")

        if len(password) < 6:
            raise ValueError("Password must contain at least 6 characters")

        if len(username) > 32:
            raise ValueError("Username must contain no more than 32 characters")

        if len(password) > 64:
            raise ValueError("Password must contain no more than 64 characters")

        existing_user = self.repository.get_by_username(username)

        if existing_user is not None:
            raise UserAlreadyExistsError()

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        return self.repository.create(
            username=username,
            password_hash=password_hash,
        )
