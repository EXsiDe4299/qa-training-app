from playwright.sync_api import Page, expect


class RequestsPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def open(self):
        self.page.goto(f"{self.base_url}/requests")

    def current_username(self):
        return self.page.get_by_test_id("current-username")

    def create_request(self, title: str, description: str):
        self.page.get_by_test_id("title-input").fill(title)
        self.page.get_by_test_id("description-input").fill(description)
        self.page.get_by_test_id("create-request-submit").click()

    def request_card(self, title: str | None = None):
        card = self.page.get_by_test_id("request-card")
        if title is None:
            return card
        return card.filter(
            has=self.page.get_by_test_id("request-title").get_by_text(title, exact=True)
        )

    def empty_state(self):
        return self.page.get_by_test_id("empty-state")

    def delete_request(self, title: str):
        request_card = self.request_card(title)
        expect(request_card).to_be_visible()
        request_card.get_by_test_id("delete-request-button").click()
        expect(request_card).to_have_count(0)

    def logout(self):
        self.page.get_by_test_id("logout-button").click()

    def error_message(self):
        return self.page.get_by_test_id("error-message")
