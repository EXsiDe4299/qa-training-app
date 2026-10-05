import pytest
from backend.unit.fakes import FakeRequestRepository, FakeUserRepository


@pytest.fixture
def user_repository():
    return FakeUserRepository()


@pytest.fixture
def request_repository():
    return FakeRequestRepository()
