import allure
import requests

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Backend"),
    allure.suite("Integration tests"),
]


@allure.title("Login endpoint sets session cookie")
@allure.feature("Authentication")
@allure.story("Successful login")
def test_login_endpoint_sets_session_in_cookies(
    base_url: str,
    create_user,
):
    username = "test_username"
    password = "test_password"

    with allure.step("Create a test user"):
        user = create_user(username, password)

    with allure.step("Log in through the API"):
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )

    with allure.step("Verify response and session cookie"):
        assert response.status_code == 200
        assert "session" in response.cookies
        assert response.json() == {
            "user_id": user["id"],
            "username": username,
        }


@allure.title("Login endpoint rejects invalid password")
@allure.feature("Authentication")
@allure.story("Invalid credentials")
def test_login_endpoint_returns_error_for_invalid_password(
    base_url: str,
    create_user,
):
    username = "test_username"
    password = "test_password"

    with allure.step("Create a test user"):
        create_user(username, password)

    with allure.step("Attempt login with an invalid password"):
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "username": username,
                "password": "invalid_password",
            },
        )

    with allure.step("Verify that login is rejected"):
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"
        assert "session" not in response.cookies


@allure.title("Login endpoint rejects invalid username")
@allure.feature("Authentication")
@allure.story("Invalid credentials")
def test_login_endpoint_returns_error_for_invalid_username(
    base_url: str,
    create_user,
):
    username = "test_username"
    password = "test_password"

    with allure.step("Create a test user"):
        create_user(username, password)

    with allure.step("Attempt login with an invalid username"):
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "username": "invalid_username",
                "password": password,
            },
        )

    with allure.step("Verify that login is rejected"):
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"
        assert "session" not in response.cookies


@allure.title("Login endpoint returns 422 for missing required field")
@allure.feature("Authentication")
@allure.story("Request validation")
def test_login_endpoint_returns_422_when_required_field_is_missing(
    base_url: str,
):
    with allure.step("Send login request without password"):
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "username": "test_username",
            },
        )

    with allure.step("Verify validation response"):
        assert response.status_code == 422


@allure.title("Logout endpoint clears session")
@allure.feature("Authentication")
@allure.story("Logout")
def test_logout_endpoint_clears_session(
    base_url: str,
    authenticated_session,
    create_user,
):
    username = "test_username"
    password = "test_password"

    with allure.step("Create a test user and authenticate"):
        create_user(username, password)
        session = authenticated_session(username, password)

    with allure.step("Log out through the API"):
        response = session.post(
            f"{base_url}/api/v1/auth/logout",
        )

    with allure.step("Verify session is cleared"):
        assert response.status_code == 200
        assert response.json() == {"message": "Logged out"}
        assert "session" not in session.cookies

    with allure.step("Verify authenticated endpoint is no longer accessible"):
        me_response = session.get(
            f"{base_url}/api/v1/auth/me",
        )

        assert me_response.status_code == 401
        assert me_response.json()["detail"] == "Not authenticated"


@allure.title("Logout endpoint works without session")
@allure.feature("Authentication")
@allure.story("Logout")
def test_logout_endpoint_works_without_session(
    base_url: str,
):
    with allure.step("Send logout request without authentication"):
        response = requests.post(
            f"{base_url}/api/v1/auth/logout",
        )

    with allure.step("Verify successful logout response"):
        assert response.status_code == 200
        assert response.json() == {"message": "Logged out"}


@allure.title("Me endpoint returns current user")
@allure.feature("Authentication")
@allure.story("Current user")
def test_me_endpoint_returns_current_user(
    base_url: str,
    create_user,
    authenticated_session,
):
    username = "test_username"
    password = "test_password"

    with allure.step("Create a test user and authenticate"):
        user = create_user(username, password)
        session = authenticated_session(username, password)

    with allure.step("Request current user"):
        response = session.get(
            f"{base_url}/api/v1/auth/me",
        )

    with allure.step("Verify current user data"):
        assert response.status_code == 200
        assert response.json() == {
            "id": user["id"],
            "username": username,
        }


@allure.title("Me endpoint rejects unauthenticated user")
@allure.feature("Authentication")
@allure.story("Current user")
def test_me_endpoint_returns_error_without_session(
    base_url: str,
):
    with allure.step("Request current user without authentication"):
        response = requests.get(
            f"{base_url}/api/v1/auth/me",
        )

    with allure.step("Verify authentication error"):
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
