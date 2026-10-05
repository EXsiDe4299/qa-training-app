import bcrypt

from qa_training_app.users.interfaces import UserRepositoryABC


class AuthService:
    def __init__(self, repository: UserRepositoryABC):
        self.repository = repository

    def login(self, username: str, password: str) -> int | None:
        user = self.repository.get_by_username(username.strip())

        if user is None:
            return None

        password_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        )

        if not password_valid:
            return None

        return user.id
