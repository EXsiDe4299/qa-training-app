import allure
from playwright.sync_api import BrowserContext, Page, expect
from web.e2e.auth_helpers import register_and_login
from web.pages.requests_page import RequestsPage

pytestmark = [
    allure.epic("QA Training App"),
    allure.parent_suite("Web"),
    allure.suite("E2E tests"),
]


@allure.title("User sees empty state when there are no requests")
@allure.feature("Requests")
@allure.story("Empty state")
def test_user_sees_empty_state_when_there_are_no_requests(
    page: Page,
    base_url: str,
):
    register_and_login(
        page,
        base_url,
        "empty_state_user",
        "test_password",
    )

    requests_page = RequestsPage(page, base_url)

    with allure.step("Verify empty state"):
        expect(requests_page.empty_state()).to_be_visible()
        expect(requests_page.empty_state()).to_have_text("Заявок пока нет.")


@allure.title("User can create a request")
@allure.feature("Requests")
@allure.story("Create request")
def test_user_can_create_a_request(
    page: Page,
    base_url: str,
):
    username = "create_request_user"
    password = "test_password"
    title = "test title"
    description = "test description"

    register_and_login(page, base_url, username, password)

    requests_page = RequestsPage(page, base_url)

    with allure.step("Create a request"):
        requests_page.create_request(title, description)

    with allure.step("Verify request is displayed"):
        request_card = requests_page.request_card(title)

        expect(request_card).to_be_visible()
        expect(request_card.get_by_test_id("request-title")).to_have_text(title)
        expect(request_card.get_by_test_id("request-description")).to_have_text(
            description
        )
        expect(request_card.get_by_test_id("request-author")).to_have_text(
            f"Автор: {username}"
        )
        expect(requests_page.empty_state()).not_to_be_visible()

    with allure.step("Reload page and verify request persists"):
        page.reload()

        request_card = requests_page.request_card(title)

        expect(request_card).to_be_visible()
        expect(request_card.get_by_test_id("request-title")).to_have_text(title)
        expect(request_card.get_by_test_id("request-description")).to_have_text(
            description
        )
        expect(request_card.get_by_test_id("request-author")).to_have_text(
            f"Автор: {username}"
        )


@allure.title("Request cannot be created with whitespace title")
@allure.feature("Requests")
@allure.story("Request validation")
def test_cannot_create_request_with_whitespace_title(
    page: Page,
    base_url: str,
):
    register_and_login(
        page,
        base_url,
        "whitespace_title_user",
        "test_password",
    )

    requests_page = RequestsPage(page, base_url)

    with allure.step("Attempt to create request with whitespace title"):
        requests_page.create_request(" ", "test description")

    with allure.step("Verify validation error"):
        expect(requests_page.error_message()).to_contain_text("Title cannot be empty")
        expect(requests_page.empty_state()).to_be_visible()


@allure.title("Request cannot be created with whitespace description")
@allure.feature("Requests")
@allure.story("Request validation")
def test_cannot_create_request_with_whitespace_description(
    page: Page,
    base_url: str,
):
    register_and_login(
        page,
        base_url,
        "whitespace_description_user",
        "test_password",
    )

    requests_page = RequestsPage(page, base_url)

    with allure.step("Attempt to create request with whitespace description"):
        requests_page.create_request("test title", " ")

    with allure.step("Verify validation error"):
        expect(requests_page.error_message()).to_contain_text(
            "Description cannot be empty"
        )
        expect(requests_page.empty_state()).to_be_visible()


@allure.title("User can delete own request")
@allure.feature("Requests")
@allure.story("Delete request")
def test_user_can_delete_own_request(
    page: Page,
    base_url: str,
):
    register_and_login(
        page,
        base_url,
        "delete_request_user",
        "test_password",
    )

    requests_page = RequestsPage(page, base_url)

    with allure.step("Create a request"):
        requests_page.create_request(
            "test title",
            "test description",
        )

    with allure.step("Delete the request"):
        requests_page.delete_request("test title")

    with allure.step("Verify request is deleted"):
        expect(requests_page.empty_state()).to_be_visible()

    with allure.step("Reload page and verify request is still absent"):
        page.reload()

        expect(requests_page.empty_state()).to_be_visible()
        expect(requests_page.request_card("test title")).not_to_be_visible()


@allure.title("User cannot see delete button on another user's request")
@allure.feature("Requests")
@allure.story("Request permissions")
def test_user_cannot_see_delete_button_on_another_users_request(
    page: Page,
    base_url: str,
):
    first_username = "first_username"
    first_password = "first_password"
    second_username = "second_username"
    second_password = "second_password"
    title = "test title"
    description = "test description"

    register_and_login(
        page,
        base_url,
        first_username,
        first_password,
    )

    requests_page = RequestsPage(page, base_url)

    with allure.step("Create request as the first user"):
        requests_page.create_request(title, description)

    with allure.step("Verify owner can see delete button"):
        request_card = requests_page.request_card(title)
        expect(request_card.get_by_test_id("delete-request-button")).to_be_visible()

    with allure.step("Log out and log in as the second user"):
        requests_page.logout()
        expect(page).to_have_url(f"{base_url}/login")

        register_and_login(
            page,
            base_url,
            second_username,
            second_password,
        )

    with allure.step("Verify second user cannot delete another user's request"):
        request_card = requests_page.request_card(title)

        expect(request_card).to_be_visible()
        expect(request_card.get_by_test_id("request-author")).to_have_text(
            f"Автор: {first_username}"
        )
        expect(request_card.get_by_test_id("delete-request-button")).not_to_be_visible()


@allure.title("Session is shared across tabs and cleared after logout")
@allure.feature("Authentication")
@allure.story("Session management")
def test_session_is_shared_across_tabs_and_cleared_after_logout(
    page: Page,
    base_url: str,
    context: BrowserContext,
):
    username = "session_user"
    password = "test_password"

    register_and_login(
        page,
        base_url,
        username,
        password,
    )

    with allure.step("Open requests page in a second tab"):
        new_page = context.new_page()
        new_page.goto(f"{base_url}/requests")

        expect(new_page).to_have_url(f"{base_url}/requests")
        expect(new_page.get_by_test_id("current-username")).to_have_text(username)

    with allure.step("Log out from the second tab"):
        RequestsPage(new_page, base_url).logout()
        expect(new_page).to_have_url(f"{base_url}/login")

    with allure.step("Verify logout is reflected in the first tab"):
        page.reload()
        expect(page).to_have_url(f"{base_url}/login")
