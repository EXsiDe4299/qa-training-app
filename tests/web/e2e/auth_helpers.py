import allure
from playwright.sync_api import Page, expect
from web.pages.login_page import LoginPage
from web.pages.register_page import RegisterPage


@allure.step("Register user {username}")
def register_user(
    page: Page,
    base_url: str,
    username: str,
    password: str,
) -> None:
    login_page = LoginPage(page, base_url)
    register_page = RegisterPage(page, base_url)

    login_page.open()
    login_page.go_to_register()
    register_page.register(username, password)


@allure.step("Register and log in as {username}")
def register_and_login(
    page: Page,
    base_url: str,
    username: str,
    password: str,
) -> None:
    register_user(page, base_url, username, password)
    expect(page).to_have_url(f"{base_url}/login")
    LoginPage(page, base_url).login(username, password)
    expect(page).to_have_url(f"{base_url}/requests")
