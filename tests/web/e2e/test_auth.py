import allure
from playwright.sync_api import Page, expect
from web.e2e.auth_helpers import register_and_login, register_user
from web.pages.login_page import LoginPage
from web.pages.register_page import RegisterPage
from web.pages.requests_page import RequestsPage

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Web"),
    allure.suite("E2E tests"),
]


@allure.title("User can register and log in")
@allure.feature("Authentication")
@allure.story("Successful registration and login")
def test_user_can_register_and_login(
    page: Page,
    base_url: str,
):
    username = "test_username"
    password = "test_password"

    register_and_login(page, base_url, username, password)

    with allure.step("Verify current username"):
        requests_page = RequestsPage(page, base_url)
        expect(requests_page.current_username()).to_have_text(username)


@allure.title("User can navigate between login and registration")
@allure.feature("Authentication")
@allure.story("Navigation")
def test_user_can_navigate_between_login_and_register(
    page: Page,
    base_url: str,
):
    login_page = LoginPage(page, base_url)
    register_page = RegisterPage(page, base_url)

    with allure.step("Open login page"):
        login_page.open()
        expect(page.get_by_test_id("login-form")).to_be_visible()

    with allure.step("Open registration page"):
        login_page.go_to_register()
        expect(page.get_by_test_id("register-form")).to_be_visible()

    with allure.step("Return to login page"):
        register_page.go_to_login()
        expect(page.get_by_test_id("login-form")).to_be_visible()


@allure.title("Registration rejects short username")
@allure.feature("Authentication")
@allure.story("Registration validation")
def test_register_rejects_short_username(
    page: Page,
    base_url: str,
):
    register_page = RegisterPage(page, base_url)

    register_user(page, base_url, "ab", "test_password")

    with allure.step("Verify username validation error"):
        expect(page).to_have_url(f"{base_url}/register")
        expect(register_page.error_message()).to_contain_text(
            "Username must contain at least 3 characters"
        )


@allure.title("Registration rejects short password")
@allure.feature("Authentication")
@allure.story("Registration validation")
def test_register_rejects_short_password(
    page: Page,
    base_url: str,
):
    register_page = RegisterPage(page, base_url)

    register_user(page, base_url, "test_username", "qwert")

    with allure.step("Verify password validation error"):
        expect(page).to_have_url(f"{base_url}/register")
        expect(register_page.error_message()).to_contain_text(
            "Password must contain at least 6 characters"
        )


@allure.title("Registration rejects long username")
@allure.feature("Authentication")
@allure.story("Registration validation")
def test_register_rejects_long_username(
    page: Page,
    base_url: str,
):
    register_page = RegisterPage(page, base_url)

    register_user(page, base_url, "a" * 33, "test_password")

    with allure.step("Verify username validation error"):
        expect(page).to_have_url(f"{base_url}/register")
        expect(register_page.error_message()).to_contain_text(
            "Username must contain no more than 32 characters"
        )


@allure.title("Registration rejects long password")
@allure.feature("Authentication")
@allure.story("Registration validation")
def test_register_rejects_long_password(
    page: Page,
    base_url: str,
):
    register_page = RegisterPage(page, base_url)

    register_user(page, base_url, "test_username", "a" * 65)

    with allure.step("Verify password validation error"):
        expect(page).to_have_url(f"{base_url}/register")
        expect(register_page.error_message()).to_contain_text(
            "Password must contain no more than 64 characters"
        )


@allure.title("Registration rejects duplicate username")
@allure.feature("Authentication")
@allure.story("Duplicate username")
def test_register_rejects_duplicate_username(
    page: Page,
    base_url: str,
):
    username = "test_username"
    password = "test_password"

    login_page = LoginPage(page, base_url)
    register_page = RegisterPage(page, base_url)

    register_user(page, base_url, username, password)

    with allure.step("Return to registration page"):
        expect(page).to_have_url(f"{base_url}/login")
        login_page.go_to_register()

    with allure.step("Attempt to register duplicate username"):
        register_page.register(username, password)

    with allure.step("Verify duplicate username error"):
        expect(page).to_have_url(f"{base_url}/register")
        expect(register_page.error_message()).to_contain_text("Username already exists")


@allure.title("Login rejects invalid credentials")
@allure.feature("Authentication")
@allure.story("Invalid credentials")
def test_login_rejects_invalid_credentials(
    page: Page,
    base_url: str,
):
    login_page = LoginPage(page, base_url)

    register_user(page, base_url, "test_username", "test_password")

    with allure.step("Attempt login with invalid credentials"):
        expect(page).to_have_url(f"{base_url}/login")
        login_page.login("invalid_username", "invalid_password")

    with allure.step("Verify login error"):
        expect(page).to_have_url(f"{base_url}/login")
        expect(login_page.error_message()).to_contain_text(
            "Invalid username or password"
        )


@allure.title("Unauthenticated user is redirected to login")
@allure.feature("Authentication")
@allure.story("Access control")
def test_unauthenticated_user_is_redirected_to_login(
    page: Page,
    base_url: str,
):
    with allure.step("Open protected requests page"):
        RequestsPage(page, base_url).open()

    with allure.step("Verify redirect to login"):
        expect(page).to_have_url(f"{base_url}/login")


@allure.title("User can log out")
@allure.feature("Authentication")
@allure.story("Logout")
def test_user_can_logout(
    page: Page,
    base_url: str,
):
    register_and_login(
        page,
        base_url,
        "test_username",
        "test_password",
    )

    requests_page = RequestsPage(page, base_url)

    with allure.step("Log out"):
        requests_page.logout()
        expect(page).to_have_url(f"{base_url}/login")

    with allure.step("Verify protected page remains inaccessible"):
        requests_page.open()
        expect(page).to_have_url(f"{base_url}/login")
