import allure
from appium.webdriver.webdriver import WebDriver
from mobile.pages.auth_page import AuthPage

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Mobile"),
    allure.suite("E2E tests"),
]


@allure.title("User can register and log in through mobile app")
@allure.feature("Authentication")
@allure.story("Successful registration and login")
def test_user_can_register_and_login(driver: WebDriver):
    username = "test_username"
    password = "test_password"

    auth_page = AuthPage(driver)

    auth_page.open_registration()
    auth_page.register(username, password)
    auth_page.login(username, password)
    auth_page.wait_until_logged_in()
