from qa_training_app.requests.interfaces import RequestRepositoryABC
from qa_training_app.requests.schemas import RequestItem


class RequestNotFoundError(Exception):
    pass


class RequestPermissionError(Exception):
    pass


class RequestService:
    def __init__(self, repository: RequestRepositoryABC):
        self.repository = repository

    def get_all(self) -> list[RequestItem]:
        return self.repository.get_all()

    def get_by_id(self, request_id: int) -> RequestItem | None:
        return self.repository.get_by_id(request_id)

    def create(
        self,
        title: str,
        description: str,
        author_id: int,
    ) -> RequestItem:
        title = title.strip()
        description = description.strip()

        if not title:
            raise ValueError("Title cannot be empty")

        if not description:
            raise ValueError("Description cannot be empty")

        return self.repository.create(
            title=title,
            description=description,
            author_id=author_id,
        )

    def delete(
        self,
        request_id: int,
        user_id: int,
    ) -> None:
        request = self.repository.get_by_id(request_id)

        if request is None:
            raise RequestNotFoundError()

        if request.author_id != user_id:
            raise RequestPermissionError()

        self.repository.delete(request_id)
