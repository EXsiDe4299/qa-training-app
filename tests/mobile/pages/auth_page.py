import allure
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from mobile.e2e.conftest import APP_ID
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class AuthPage:
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _id(self, resource_id: str):
        return AppiumBy.ID, f"{APP_ID}:id/{resource_id}"

    @allure.step("Open registration form")
    def open_registration(self) -> None:
        self.wait.until(
            expected_conditions.element_to_be_clickable(
                self._id("button_open_register")
            )
        ).click()

    @allure.step("Register user {username}")
    def register(
        self,
        username: str,
        password: str,
    ) -> None:
        username_field = self.wait.until(
            expected_conditions.visibility_of_element_located(
                self._id("input_register_username")
            )
        )
        password_field = self.wait.until(
            expected_conditions.visibility_of_element_located(
                self._id("input_register_password")
            )
        )
        repeat_password_field = self.wait.until(
            expected_conditions.visibility_of_element_located(
                self._id("input_register_password_confirm")
            )
        )

        username_field.send_keys(username)
        password_field.send_keys(password)
        repeat_password_field.send_keys(password)

        self.wait.until(
            expected_conditions.element_to_be_clickable(self._id("button_register"))
        ).click()

    @allure.step("Log in as {username}")
    def login(
        self,
        username: str,
        password: str,
    ) -> None:
        username_field = self.wait.until(
            expected_conditions.visibility_of_element_located(
                self._id("input_login_username")
            )
        )
        password_field = self.wait.until(
            expected_conditions.visibility_of_element_located(
                self._id("input_login_password")
            )
        )

        username_field.send_keys(username)
        password_field.send_keys(password)

        self.wait.until(
            expected_conditions.element_to_be_clickable(self._id("button_login"))
        ).click()

    @allure.step("Verify successful login")
    def wait_until_logged_in(self) -> None:
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                self._id("button_create_request")
            )
        )
