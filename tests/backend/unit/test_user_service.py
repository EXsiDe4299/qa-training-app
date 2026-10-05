import allure
import bcrypt
import pytest
from backend.unit.fakes import FakeUserRepository

from qa_training_app.users.service import UserAlreadyExistsError, UserService

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Backend"),
    allure.suite("Unit tests"),
]


@pytest.mark.parametrize(
    "username",
    (
        "a" * 3,
        "a" * 4,
        "a" * 31,
        "a" * 32,
    ),
)
@allure.title("Registration accepts valid username")
@allure.feature("User registration")
@allure.story("Valid username")
def test_register_accepts_valid_username(
    user_repository: FakeUserRepository,
    username: str,
):
    password = "test_password"

    service = UserService(user_repository)

    with allure.step("Register a user"):
        user = service.register(username, password)

    with allure.step("Verify registered user and password hash"):
        user_in_db = user_repository.get_by_username(username)

        assert user_in_db is not None
        assert user_in_db.id == user.id
        assert user.username == username
        assert bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        )


@allure.title("Registration strips username whitespace")
@allure.feature("User registration")
@allure.story("Username normalization")
def test_register_strips_username(
    user_repository: FakeUserRepository,
):
    username = " test_username "
    password = "test_password"

    service = UserService(user_repository)

    with allure.step("Register a user with surrounding whitespace"):
        user = service.register(username, password)

    with allure.step("Verify that username was normalized"):
        assert user.username == username.strip()


@allure.title("Registration rejects username that becomes empty")
@allure.feature("User registration")
@allure.story("Username validation")
def test_register_rejects_username_that_becomes_empty_after_stripping(
    user_repository: FakeUserRepository,
):
    service = UserService(user_repository)

    with (
        allure.step("Attempt to register whitespace-only username"),
        pytest.raises(ValueError),
    ):
        service.register("   ", "test_password")

    with allure.step("Verify that the user was not created"):
        assert user_repository.get_users() == []


@pytest.mark.parametrize(
    "username",
    (
        "юзернейм",
        "test username",
        "test-username",
        "test#username",
    ),
)
@allure.title("Registration rejects invalid username characters")
@allure.feature("User registration")
@allure.story("Username validation")
def test_register_returns_error_for_invalid_username_characters(
    user_repository: FakeUserRepository,
    username: str,
):
    service = UserService(user_repository)

    with (
        allure.step("Attempt to register an invalid username"),
        pytest.raises(ValueError) as exc,
    ):
        service.register(username, "test_password")

    with allure.step("Verify validation error"):
        assert exc.value.args[0] == (
            "Username must contain only Latin letters, digits, and underscores."
        )
        assert user_repository.get_by_username(username) is None


@allure.title("Registration rejects short username")
@allure.feature("User registration")
@allure.story("Username validation")
def test_register_returns_error_for_short_username(
    user_repository: FakeUserRepository,
):
    service = UserService(user_repository)

    with (
        allure.step("Attempt to register a username shorter than 3 characters"),
        pytest.raises(ValueError) as exc,
    ):
        service.register("a" * 2, "test_password")

    with allure.step("Verify validation error"):
        assert exc.value.args[0] == "Username must contain at least 3 characters"
        assert user_repository.get_by_username("aa") is None


@allure.title("Registration rejects long username")
@allure.feature("User registration")
@allure.story("Username validation")
def test_register_returns_error_for_long_username(
    user_repository: FakeUserRepository,
):
    username = "a" * 33
    service = UserService(user_repository)

    with (
        allure.step("Attempt to register a username longer than 32 characters"),
        pytest.raises(ValueError) as exc,
    ):
        service.register(username, "test_password")

    with allure.step("Verify validation error"):
        assert exc.value.args[0] == "Username must contain no more than 32 characters"
        assert user_repository.get_by_username(username) is None


@pytest.mark.parametrize(
    "password",
    (
        "a" * 6,
        "a" * 7,
        "a" * 63,
        "a" * 64,
    ),
)
@allure.title("Registration accepts valid password")
@allure.feature("User registration")
@allure.story("Valid password")
def test_register_accepts_valid_password(
    user_repository: FakeUserRepository,
    password: str,
):
    username = "test_username"

    service = UserService(user_repository)

    with allure.step("Register a user with a valid password"):
        user = service.register(username, password)

    with allure.step("Verify password hash"):
        user_in_db = user_repository.get_by_username(username)

        assert user_in_db is not None
        assert user_in_db.id == user.id
        assert user.username == username
        assert bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        )


@pytest.mark.parametrize(
    "password",
    (
        "пароль",
        "test password",
        "test(password",
        "test-password",
    ),
)
@allure.title("Registration rejects invalid password characters")
@allure.feature("User registration")
@allure.story("Password validation")
def test_register_returns_error_for_invalid_password_characters(
    user_repository: FakeUserRepository,
    password: str,
):
    service = UserService(user_repository)

    with (
        allure.step("Attempt to register an invalid password"),
        pytest.raises(ValueError) as exc,
    ):
        service.register("test_username", password)

    with allure.step("Verify validation error"):
        assert exc.value.args[0] == (
            "Password must contain only Latin letters, digits, and special characters."
        )
        assert user_repository.get_by_username("test_username") is None


@allure.title("Registration rejects short password")
@allure.feature("User registration")
@allure.story("Password validation")
def test_register_returns_error_for_short_password(
    user_repository: FakeUserRepository,
):
    service = UserService(user_repository)

    with (
        allure.step("Attempt to register a password shorter than 6 characters"),
        pytest.raises(ValueError) as exc,
    ):
        service.register("test_username", "a" * 5)

    with allure.step("Verify validation error"):
        assert exc.value.args[0] == "Password must contain at least 6 characters"
        assert user_repository.get_by_username("test_username") is None


@allure.title("Registration rejects long password")
@allure.feature("User registration")
@allure.story("Password validation")
def test_register_returns_error_for_long_password(
    user_repository: FakeUserRepository,
):
    service = UserService(user_repository)
    password = "a" * 65

    with (
        allure.step("Attempt to register a password longer than 64 characters"),
        pytest.raises(ValueError) as exc,
    ):
        service.register("test_username", password)

    with allure.step("Verify validation error"):
        assert exc.value.args[0] == "Password must contain no more than 64 characters"
        assert user_repository.get_by_username("test_username") is None


@allure.title("Registration rejects duplicate username")
@allure.feature("User registration")
@allure.story("Duplicate username")
def test_register_returns_error_for_existing_username(
    user_repository: FakeUserRepository,
):
    username = "test_username"
    password = "test_password"

    service = UserService(user_repository)

    with allure.step("Register the first user"):
        service.register(username, password)

    with (
        allure.step("Attempt to register the same username"),
        pytest.raises(UserAlreadyExistsError),
    ):
        service.register(username, password)

    with allure.step("Verify that only one user exists"):
        assert len(user_repository.get_users()) == 1


@allure.title("Registration rejects duplicate normalized username")
@allure.feature("User registration")
@allure.story("Duplicate username")
def test_register_returns_error_for_existing_username_after_stripping(
    user_repository: FakeUserRepository,
):
    username = "test_username"
    password = "test_password"

    service = UserService(user_repository)

    with allure.step("Register the first user"):
        service.register(username, password)

    with (
        allure.step("Attempt to register the same username with whitespace"),
        pytest.raises(UserAlreadyExistsError),
    ):
        service.register(f" {username} ", password)

    with allure.step("Verify that only one user exists"):
        assert len(user_repository.get_users()) == 1
