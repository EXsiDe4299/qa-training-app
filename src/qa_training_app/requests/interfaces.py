from abc import ABC, abstractmethod

from qa_training_app.requests.schemas import RequestItem


class RequestRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> list[RequestItem]:
        pass

    @abstractmethod
    def get_by_id(self, request_id: int) -> RequestItem | None:
        pass

    @abstractmethod
    def create(
        self,
        title: str,
        description: str,
        author_id: int,
    ) -> RequestItem:
        pass

    @abstractmethod
    def delete(self, request_id: int) -> None:
        pass
