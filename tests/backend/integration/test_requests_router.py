from sqlite3 import Connection

import allure
import requests

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Backend"),
    allure.suite("Integration tests"),
]


@allure.title("Get requests endpoint returns requests from all users")
@allure.feature("Requests")
@allure.story("List requests")
def test_get_requests_endpoint_returns_requests_from_all_users(
    base_url: str,
    create_user,
    authenticated_session,
    create_request,
):
    first_username = "first_username"
    first_password = "first_password"
    second_username = "second_username"
    second_password = "second_password"

    with allure.step("Create two users"):
        first_user = create_user(first_username, first_password)
        second_user = create_user(second_username, second_password)

    with allure.step("Create requests for both users"):
        first_request = create_request(
            "first_title",
            "first_description",
            first_user["id"],
        )
        second_request = create_request(
            "second_title",
            "second_description",
            second_user["id"],
        )

    with allure.step("Authenticate the first user"):
        session = authenticated_session(
            first_username,
            first_password,
        )

    with allure.step("Request all requests"):
        response = session.get(
            f"{base_url}/api/v1/requests",
        )

    with allure.step("Verify requests from both users are returned"):
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": second_request["id"],
                "title": "second_title",
                "description": "second_description",
                "author_id": second_user["id"],
                "author_username": second_username,
            },
            {
                "id": first_request["id"],
                "title": "first_title",
                "description": "first_description",
                "author_id": first_user["id"],
                "author_username": first_username,
            },
        ]


@allure.title("Get requests endpoint rejects unauthenticated user")
@allure.feature("Requests")
@allure.story("Authentication")
def test_get_requests_endpoint_returns_error_without_session(
    base_url: str,
):
    with allure.step("Request all requests without authentication"):
        response = requests.get(
            f"{base_url}/api/v1/requests",
        )

    with allure.step("Verify authentication error"):
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@allure.title("Create request endpoint creates a request")
@allure.feature("Requests")
@allure.story("Create request")
def test_create_request_endpoint_creates_request(
    base_url: str,
    connection: Connection,
    create_user,
    authenticated_session,
):
    username = "test_username"
    password = "test_password"
    title = "test_title"
    description = "test_description"

    with allure.step("Create a test user and authenticate"):
        user = create_user(username, password)
        session = authenticated_session(username, password)

    with allure.step("Create a request through the API"):
        response = session.post(
            f"{base_url}/api/v1/requests",
            json={
                "title": title,
                "description": description,
            },
        )

    with allure.step("Verify API response"):
        assert response.status_code == 201

        response_data = response.json()

        assert response_data["title"] == title
        assert response_data["description"] == description
        assert response_data["author_id"] == user["id"]
        assert response_data["author_username"] == username

    with allure.step("Verify request was persisted in the database"):
        request = connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (response_data["id"],),
        ).fetchone()

        assert request["title"] == title
        assert request["description"] == description
        assert request["author_id"] == user["id"]


@allure.title("Create request endpoint returns 422 for missing field")
@allure.feature("Requests")
@allure.story("Request validation")
def test_create_request_endpoint_returns_422_when_required_field_is_missing(
    base_url: str,
    create_user,
    authenticated_session,
):
    with allure.step("Create a test user and authenticate"):
        create_user("test_username", "test_password")
        session = authenticated_session(
            "test_username",
            "test_password",
        )

    with allure.step("Create a request without description"):
        response = session.post(
            f"{base_url}/api/v1/requests",
            json={
                "title": "test_title",
            },
        )

    with allure.step("Verify validation response"):
        assert response.status_code == 422


@allure.title("Create request endpoint rejects empty title")
@allure.feature("Requests")
@allure.story("Request validation")
def test_create_request_endpoint_returns_error_for_empty_title(
    base_url: str,
    connection: Connection,
    create_user,
    authenticated_session,
):
    with allure.step("Create a test user and authenticate"):
        user = create_user("test_username", "test_password")
        session = authenticated_session(
            "test_username",
            "test_password",
        )

    with allure.step("Create a request with empty title"):
        response = session.post(
            f"{base_url}/api/v1/requests",
            json={
                "title": "",
                "description": "test_description",
            },
        )

    with allure.step("Verify validation error"):
        assert response.status_code == 400
        assert response.json()["detail"] == "Title cannot be empty"

    with allure.step("Verify that no request was created"):
        requests_count = connection.execute(
            "SELECT COUNT(*) FROM requests WHERE author_id = ?",
            (user["id"],),
        ).fetchone()[0]

        assert requests_count == 0


@allure.title("Create request endpoint rejects empty description")
@allure.feature("Requests")
@allure.story("Request validation")
def test_create_request_endpoint_returns_error_for_empty_description(
    base_url: str,
    connection: Connection,
    create_user,
    authenticated_session,
):
    with allure.step("Create a test user and authenticate"):
        user = create_user("test_username", "test_password")
        session = authenticated_session(
            "test_username",
            "test_password",
        )

    with allure.step("Create a request with empty description"):
        response = session.post(
            f"{base_url}/api/v1/requests",
            json={
                "title": "test_title",
                "description": "",
            },
        )

    with allure.step("Verify validation error"):
        assert response.status_code == 400
        assert response.json()["detail"] == "Description cannot be empty"

    with allure.step("Verify that no request was created"):
        requests_count = connection.execute(
            "SELECT COUNT(*) FROM requests WHERE author_id = ?",
            (user["id"],),
        ).fetchone()[0]

        assert requests_count == 0


@allure.title("Create request endpoint rejects unauthenticated user")
@allure.feature("Requests")
@allure.story("Authentication")
def test_create_request_endpoint_returns_error_without_session(
    base_url: str,
):
    with allure.step("Attempt to create a request without authentication"):
        response = requests.post(
            f"{base_url}/api/v1/requests",
            json={
                "title": "test_title",
                "description": "test_description",
            },
        )

    with allure.step("Verify authentication error"):
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@allure.title("Get request endpoint returns request")
@allure.feature("Requests")
@allure.story("Get request")
def test_get_request_endpoint_returns_request(
    base_url: str,
    create_user,
    authenticated_session,
    create_request,
):
    username = "test_username"
    password = "test_password"
    title = "test_title"
    description = "test_description"

    with allure.step("Create a test user and request"):
        user = create_user(username, password)
        request = create_request(
            title,
            description,
            user["id"],
        )

    with allure.step("Authenticate the user"):
        session = authenticated_session(username, password)

    with allure.step("Request the created request"):
        response = session.get(
            f"{base_url}/api/v1/requests/{request['id']}",
        )

    with allure.step("Verify request data"):
        assert response.status_code == 200
        assert response.json() == {
            "id": request["id"],
            "title": title,
            "description": description,
            "author_id": user["id"],
            "author_username": username,
        }


@allure.title("Get request endpoint returns 404 for nonexistent request")
@allure.feature("Requests")
@allure.story("Get request")
def test_get_request_endpoint_returns_error_for_nonexistent_request(
    base_url: str,
    create_user,
    authenticated_session,
):
    with allure.step("Create a test user and authenticate"):
        create_user("test_username", "test_password")
        session = authenticated_session(
            "test_username",
            "test_password",
        )

    with allure.step("Request a nonexistent request"):
        response = session.get(
            f"{base_url}/api/v1/requests/123",
        )

    with allure.step("Verify not found response"):
        assert response.status_code == 404
        assert response.json()["detail"] == "Request not found"


@allure.title("Get request endpoint rejects unauthenticated user")
@allure.feature("Requests")
@allure.story("Authentication")
def test_get_request_endpoint_returns_error_without_session(
    base_url: str,
):
    with allure.step("Request a request without authentication"):
        response = requests.get(
            f"{base_url}/api/v1/requests/123",
        )

    with allure.step("Verify authentication error"):
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@allure.title("Delete request endpoint deletes own request")
@allure.feature("Requests")
@allure.story("Delete request")
def test_delete_request_endpoint_deletes_own_request(
    base_url: str,
    connection: Connection,
    create_user,
    authenticated_session,
    create_request,
):
    with allure.step("Create a test user and request"):
        user = create_user("test_username", "test_password")
        request = create_request(
            "test_title",
            "test_description",
            user["id"],
        )

    with allure.step("Authenticate the user"):
        session = authenticated_session(
            "test_username",
            "test_password",
        )

    with allure.step("Delete the request"):
        response = session.delete(
            f"{base_url}/api/v1/requests/{request['id']}",
        )

    with allure.step("Verify successful deletion"):
        assert response.status_code == 200
        assert response.json() == {"message": "Request deleted"}

    with allure.step("Verify the request was removed from the database"):
        deleted_request = connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (request["id"],),
        ).fetchone()

        assert deleted_request is None

    with allure.step("Verify the request is no longer available through the API"):
        get_response = session.get(
            f"{base_url}/api/v1/requests/{request['id']}",
        )

        assert get_response.status_code == 404
        assert get_response.json()["detail"] == "Request not found"


@allure.title("Delete request endpoint rejects non-owner")
@allure.feature("Requests")
@allure.story("Request permissions")
def test_delete_request_endpoint_returns_error_for_nonowner(
    base_url: str,
    connection: Connection,
    create_user,
    authenticated_session,
    create_request,
):
    with allure.step("Create two users"):
        first_user = create_user(
            "first_username",
            "first_password",
        )
        create_user(
            "second_username",
            "second_password",
        )

    with allure.step("Create a request owned by the first user"):
        request = create_request(
            "test_title",
            "test_description",
            first_user["id"],
        )

    with allure.step("Authenticate as the second user"):
        session = authenticated_session(
            "second_username",
            "second_password",
        )

    with allure.step("Attempt to delete another user's request"):
        response = session.delete(
            f"{base_url}/api/v1/requests/{request['id']}",
        )

    with allure.step("Verify permission error"):
        assert response.status_code == 403
        assert response.json()["detail"] == "You cannot delete this request"

    with allure.step("Verify that the request was not deleted"):
        request_after_delete = connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (request["id"],),
        ).fetchone()

        assert request_after_delete is not None


@allure.title("Delete request endpoint returns 404 for nonexistent request")
@allure.feature("Requests")
@allure.story("Delete request")
def test_delete_request_endpoint_returns_error_for_nonexistent_request(
    base_url: str,
    create_user,
    authenticated_session,
):
    with allure.step("Create a test user and authenticate"):
        create_user("test_username", "test_password")
        session = authenticated_session(
            "test_username",
            "test_password",
        )

    with allure.step("Attempt to delete a nonexistent request"):
        response = session.delete(
            f"{base_url}/api/v1/requests/123",
        )

    with allure.step("Verify not found response"):
        assert response.status_code == 404
        assert response.json()["detail"] == "Request not found"


@allure.title("Delete request endpoint rejects unauthenticated user")
@allure.feature("Requests")
@allure.story("Authentication")
def test_delete_request_endpoint_returns_error_without_session(
    base_url: str,
):
    with allure.step("Attempt to delete a request without authentication"):
        response = requests.delete(
            f"{base_url}/api/v1/requests/123",
        )

    with allure.step("Verify authentication error"):
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
