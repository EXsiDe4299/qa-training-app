import allure
import bcrypt
from backend.unit.fakes import FakeUserRepository

from qa_training_app.auth.service import AuthService

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Backend"),
    allure.suite("Unit tests"),
]


@allure.title("Login accepts valid credentials")
@allure.feature("Authentication")
@allure.story("Successful login")
def test_login_accepts_valid_credentials(user_repository: FakeUserRepository):
    username = "test_username"
    password = "test_password"

    with allure.step("Create a user with a valid password"):
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user = user_repository.create(username, password_hash)

    service = AuthService(user_repository)

    with allure.step("Log in with valid credentials"):
        result = service.login(username, password)

    with allure.step("Verify that the user ID is returned"):
        assert result == user.id


@allure.title("Login strips username whitespace")
@allure.feature("Authentication")
@allure.story("Username normalization")
def test_login_strips_username(user_repository: FakeUserRepository):
    username = " test_username "
    password = "test_password"

    with allure.step("Create a user with a normalized username"):
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user = user_repository.create(username.strip(), password_hash)

    service = AuthService(user_repository)

    with allure.step("Log in with a username containing whitespace"):
        result = service.login(username, password)

    with allure.step("Verify that the normalized username is accepted"):
        assert result == user.id


@allure.title("Login rejects invalid username")
@allure.feature("Authentication")
@allure.story("Invalid credentials")
def test_login_rejects_invalid_username(user_repository: FakeUserRepository):
    username = "test_username"
    password = "test_password"
    invalid_username = "invalid_username"

    with allure.step("Create a valid user"):
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user_repository.create(username, password_hash)

    service = AuthService(user_repository)

    with allure.step("Attempt to log in with an invalid username"):
        result = service.login(invalid_username, password)

    with allure.step("Verify that login is rejected"):
        assert result is None


@allure.title("Login rejects invalid password")
@allure.feature("Authentication")
@allure.story("Invalid credentials")
def test_login_rejects_invalid_password(user_repository: FakeUserRepository):
    username = "test_username"
    password = "test_password"
    invalid_password = "invalid_password"

    with allure.step("Create a valid user"):
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user_repository.create(username, password_hash)

    service = AuthService(user_repository)

    with allure.step("Attempt to log in with an invalid password"):
        result = service.login(username, invalid_password)

    with allure.step("Verify that login is rejected"):
        assert result is None


@allure.title("Login rejects nonexistent user")
@allure.feature("Authentication")
@allure.story("Invalid credentials")
def test_login_rejects_nonexistent_user(user_repository: FakeUserRepository):
    username = "test_username"
    password = "test_password"

    service = AuthService(user_repository)

    with allure.step("Attempt to log in with a nonexistent user"):
        result = service.login(username, password)

    with allure.step("Verify that login is rejected"):
        assert result is None
