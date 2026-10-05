from qa_training_app.requests.interfaces import RequestRepositoryABC
from qa_training_app.requests.schemas import RequestItem
from qa_training_app.users.interfaces import UserRepositoryABC
from qa_training_app.users.schemas import User


class FakeUserRepository(UserRepositoryABC):
    def __init__(self):
        self._users: dict[int, User] = {}

    def get_by_id(self, user_id: int) -> User | None:
        user = self._users.get(user_id)
        return self._copy(user) if user else None

    def get_by_username(self, username: str) -> User | None:
        for user in self._users.values():
            if user.username == username:
                return self._copy(user)

        return None

    def create(
        self,
        username: str,
        password_hash: str,
    ) -> User:
        user_id = max(self._users, default=0) + 1

        user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
        )

        self._users[user_id] = user

        return self._copy(user)

    def get_users(self) -> list[User]:
        return [self._copy(user) for user in self._users.values()]

    @staticmethod
    def _copy(user: User) -> User:
        return User(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
        )


class FakeRequestRepository(RequestRepositoryABC):
    def __init__(self):
        self._requests: dict[int, RequestItem] = {}

    def get_all(self) -> list[RequestItem]:
        requests = [self._copy(request) for request in self._requests.values()]

        requests.sort(key=lambda request: request.id)

        return requests

    def get_by_id(
        self,
        request_id: int,
    ) -> RequestItem | None:
        request = self._requests.get(request_id)
        return self._copy(request) if request else None

    def create(
        self,
        title: str,
        description: str,
        author_id: int,
    ) -> RequestItem:
        request_id = max(self._requests, default=0) + 1

        request = RequestItem(
            id=request_id,
            title=title,
            description=description,
            author_id=author_id,
            author_username=f"test_user_{author_id}",
        )

        self._requests[request_id] = request

        return self._copy(request)

    def delete(self, request_id: int) -> None:
        self._requests.pop(request_id, None)

    @staticmethod
    def _copy(request: RequestItem) -> RequestItem:
        return RequestItem(
            id=request.id,
            title=request.title,
            description=request.description,
            author_id=request.author_id,
            author_username=f"test_user_{request.author_id}",
        )
