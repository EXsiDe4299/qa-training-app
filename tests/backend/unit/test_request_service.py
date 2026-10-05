import allure
import pytest
from backend.unit.fakes import FakeRequestRepository

from qa_training_app.requests.service import (
    RequestNotFoundError,
    RequestPermissionError,
    RequestService,
)

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Backend"),
    allure.suite("Unit tests"),
]


@allure.title("Get all requests returns all requests")
@allure.feature("Requests")
@allure.story("List requests")
def test_get_all_returns_all_requests(
    request_repository: FakeRequestRepository,
):
    with allure.step("Create two requests"):
        first_title = "test title"
        first_description = "test description"
        second_title = "another test title"
        second_description = "another test description"

        request_repository.create(
            title=first_title,
            description=first_description,
            author_id=1,
        )
        request_repository.create(
            title=second_title,
            description=second_description,
            author_id=1,
        )

    service = RequestService(request_repository)

    with allure.step("Get all requests"):
        requests = service.get_all()

    with allure.step("Verify returned requests"):
        assert len(requests) == 2
        assert requests[0].title == first_title
        assert requests[0].description == first_description
        assert requests[0].author_id == 1
        assert requests[1].title == second_title
        assert requests[1].description == second_description
        assert requests[1].author_id == 1


@allure.title("Get request by ID returns the request")
@allure.feature("Requests")
@allure.story("Get request")
def test_get_by_id_returns_request(
    request_repository: FakeRequestRepository,
):
    with allure.step("Create a request"):
        title = "test title"
        description = "test description"

        request = request_repository.create(
            title=title,
            description=description,
            author_id=1,
        )

    service = RequestService(request_repository)

    with allure.step("Get the request by ID"):
        request_from_db = service.get_by_id(request.id)

    with allure.step("Verify returned request"):
        assert request_from_db is not None
        assert request_from_db.id == request.id
        assert request_from_db.title == title
        assert request_from_db.description == description
        assert request_from_db.author_id == 1


@allure.title("Get request by ID returns None for nonexistent request")
@allure.feature("Requests")
@allure.story("Get request")
def test_get_by_id_returns_none_for_nonexistent_request(
    request_repository: FakeRequestRepository,
):
    service = RequestService(request_repository)

    with allure.step("Request a nonexistent request"):
        result = service.get_by_id(123)

    with allure.step("Verify that no request is returned"):
        assert result is None


@allure.title("Create request creates a request")
@allure.feature("Requests")
@allure.story("Create request")
def test_create_creates_request(
    request_repository: FakeRequestRepository,
):
    title = "test title"
    description = "test description"

    service = RequestService(request_repository)

    with allure.step("Create a request"):
        request = service.create(
            title=title,
            description=description,
            author_id=1,
        )

    with allure.step("Verify created request"):
        assert request.title == title
        assert request.description == description
        assert request.author_id == 1


@allure.title("Create request strips title and description")
@allure.feature("Requests")
@allure.story("Create request")
def test_create_strips_title_and_description(
    request_repository: FakeRequestRepository,
):
    title = " test title "
    description = " test description "

    service = RequestService(request_repository)

    with allure.step("Create a request with surrounding whitespace"):
        request = service.create(
            title=title,
            description=description,
            author_id=1,
        )

    with allure.step("Verify that title and description are normalized"):
        assert request.title == title.strip()
        assert request.description == description.strip()
        assert request.author_id == 1


@pytest.mark.parametrize(
    "title",
    (
        "",
        " ",
        "   ",
    ),
)
@allure.title("Create request rejects empty title")
@allure.feature("Requests")
@allure.story("Request validation")
def test_create_returns_error_for_empty_title(
    request_repository: FakeRequestRepository,
    title: str,
):
    service = RequestService(request_repository)

    with (
        allure.step("Attempt to create a request with an empty title"),
        pytest.raises(ValueError) as exc,
    ):
        service.create(
            title=title,
            description="test description",
            author_id=1,
        )

    with allure.step("Verify validation error and unchanged repository"):
        assert exc.value.args[0] == "Title cannot be empty"
        assert len(request_repository.get_all()) == 0


@pytest.mark.parametrize(
    "description",
    (
        "",
        " ",
        "   ",
    ),
)
@allure.title("Create request rejects empty description")
@allure.feature("Requests")
@allure.story("Request validation")
def test_create_returns_error_for_empty_description(
    request_repository: FakeRequestRepository,
    description: str,
):
    service = RequestService(request_repository)

    with (
        allure.step("Attempt to create a request with an empty description"),
        pytest.raises(ValueError) as exc,
    ):
        service.create(
            title="test title",
            description=description,
            author_id=1,
        )

    with allure.step("Verify validation error and unchanged repository"):
        assert exc.value.args[0] == "Description cannot be empty"
        assert len(request_repository.get_all()) == 0


@allure.title("Delete request deletes an owned request")
@allure.feature("Requests")
@allure.story("Delete request")
def test_delete_deletes_request(
    request_repository: FakeRequestRepository,
):
    with allure.step("Create a request"):
        request = request_repository.create(
            title="test title",
            description="test description",
            author_id=1,
        )

    service = RequestService(request_repository)

    with allure.step("Delete the request as its owner"):
        service.delete(request.id, request.author_id)

    with allure.step("Verify that the request was deleted"):
        assert len(request_repository.get_all()) == 0


@allure.title("Delete request raises error for nonexistent request")
@allure.feature("Requests")
@allure.story("Delete request")
def test_delete_returns_error_for_nonexistent_request(
    request_repository: FakeRequestRepository,
):
    with allure.step("Create a request"):
        request = request_repository.create(
            title="test title",
            description="test description",
            author_id=1,
        )

    service = RequestService(request_repository)

    with (
        allure.step("Attempt to delete a nonexistent request"),
        pytest.raises(RequestNotFoundError),
    ):
        service.delete(123, request.author_id)

    with allure.step("Verify that the existing request was not changed"):
        assert len(request_repository.get_all()) == 1


@allure.title("Delete request raises error for non-owner")
@allure.feature("Requests")
@allure.story("Request permissions")
def test_delete_returns_error_for_not_own_request(
    request_repository: FakeRequestRepository,
):
    with allure.step("Create a request"):
        request = request_repository.create(
            title="test title",
            description="test description",
            author_id=1,
        )

    service = RequestService(request_repository)

    with (
        allure.step("Attempt to delete the request as another user"),
        pytest.raises(RequestPermissionError),
    ):
        service.delete(request.id, 123)

    with allure.step("Verify that the request was not deleted"):
        assert len(request_repository.get_all()) == 1
