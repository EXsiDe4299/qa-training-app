from playwright.sync_api import Page, expect


class RegisterPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def open(self):
        self.page.goto(f"{self.base_url}/register")

    def fill_username(self, username):
        self.page.get_by_test_id("username-input").fill(username)

    def fill_password(self, password):
        self.page.get_by_test_id("password-input").fill(password)

    def submit(self):
        self.page.get_by_test_id("register-submit").click()

    def register(self, username, password):
        self.fill_username(username)
        self.fill_password(password)
        self.submit()

    def error_message(self):
        return self.page.get_by_test_id("error-message")

    def go_to_login(self):
        self.page.get_by_test_id("login-link").click()
        expect(self.page).to_have_url(f"{self.base_url}/login")
