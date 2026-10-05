from sqlite3 import Connection

import allure
import bcrypt
import requests

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Backend"),
    allure.suite("Integration tests"),
]


@allure.title("Registration endpoint creates a user")
@allure.feature("User registration")
@allure.story("Successful registration")
def test_register_endpoint_creates_user(
    base_url: str,
    connection: Connection,
):
    username = "test_username"
    password = "test_password"

    with allure.step("Register a user through the API"):
        response = requests.post(
            f"{base_url}/api/v1/users/register",
            json={
                "username": username,
                "password": password,
            },
        )

    with allure.step("Verify API response"):
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["username"] == username

    with allure.step("Verify user was persisted with a valid password hash"):
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        assert user["id"] == response_data["id"]
        assert user["username"] == username
        assert bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )


@allure.title("Registration endpoint returns 422 for missing field")
@allure.feature("User registration")
@allure.story("Request validation")
def test_register_endpoint_returns_422_when_required_field_is_missing(
    base_url: str,
    connection: Connection,
):
    with allure.step("Register without password"):
        response = requests.post(
            f"{base_url}/api/v1/users/register",
            json={
                "username": "test_username",
            },
        )

    with allure.step("Verify validation response and unchanged database"):
        assert response.status_code == 422

        users = connection.execute(
            "SELECT * FROM users",
        ).fetchall()

        assert users == []


@allure.title("Registration endpoint rejects invalid username")
@allure.feature("User registration")
@allure.story("Username validation")
def test_register_endpoint_returns_error_for_invalid_username(
    base_url: str,
    connection: Connection,
):
    with allure.step("Register with invalid username"):
        response = requests.post(
            f"{base_url}/api/v1/users/register",
            json={
                "username": "invalid username",
                "password": "test_password",
            },
        )

    with allure.step("Verify validation error and unchanged database"):
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Username must contain only Latin letters, digits, and underscores."
        )

        users = connection.execute(
            "SELECT * FROM users",
        ).fetchall()

        assert users == []


@allure.title("Registration endpoint rejects invalid password")
@allure.feature("User registration")
@allure.story("Password validation")
def test_register_endpoint_returns_error_for_invalid_password(
    base_url: str,
    connection: Connection,
):
    with allure.step("Register with invalid password"):
        response = requests.post(
            f"{base_url}/api/v1/users/register",
            json={
                "username": "test_username",
                "password": "пароль",
            },
        )

    with allure.step("Verify validation error and unchanged database"):
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Password must contain only Latin letters, digits, and special characters."
        )

        users = connection.execute(
            "SELECT * FROM users",
        ).fetchall()

        assert users == []


@allure.title("Registration endpoint rejects duplicate username")
@allure.feature("User registration")
@allure.story("Duplicate username")
def test_register_endpoint_returns_error_for_duplicate_username(
    base_url: str,
    connection: Connection,
    create_user,
):
    username = "test_username"
    password = "test_password"

    with allure.step("Create the first user"):
        user = create_user(username, password)

    with allure.step("Attempt to register the same username"):
        response = requests.post(
            f"{base_url}/api/v1/users/register",
            json={
                "username": username,
                "password": password,
            },
        )

    with allure.step("Verify duplicate error and unchanged database"):
        assert response.status_code == 409
        assert response.json()["detail"] == "Username already exists"

        users = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchall()

        assert len(users) == 1
        assert users[0]["id"] == user["id"]
