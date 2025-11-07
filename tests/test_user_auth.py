from urllib.parse import urlparse

from tests.endpoints import Auth
from playwright.sync_api import Page

from tests.messages import Message
from tests.testcase_helper import log_test_result
from pytest_check import check


def _login(page: Page, payload: dict):
    page.wait_for_load_state("networkidle")
    page.goto(Auth.LOGIN)
    page.wait_for_selector("input[name='username']", state="visible", timeout=10000)
    page.fill("input[type='text'][name='username']", payload["username"])
    page.fill("input[type='password'][name='password']", payload["password"])
    with page.expect_response("**/auth/login") as resp_info:
        page.click("button[type='submit']")

    response = resp_info.value
    assert response.status == 200, f"Login failed ({response.status})"
    return response


@log_test_result(test_case_ids="TC1")
def test_login(page: Page, test_factory, base_data, test_report_file: str):
    user, password = test_factory.create_user(role_id=base_data["role_ids"]['user'])

    login_page = Auth.LOGIN
    page.goto(login_page)

    page.fill("input[type='text'][name='username']", user.username)
    page.fill("input[type='password'][name='password']", password)
    with page.expect_response("**/auth/login") as resp_info:
        page.click("button[type='submit']")

    page.wait_for_url("**/home")

    response = resp_info.value

    actual_status = str(response.status)
    actual_path = urlparse(page.url).path

    return [
        (Message.STATUS, "200", actual_status),
        (Message.URL_PATH, "/home", actual_path)
    ]


@log_test_result(test_case_ids="TC2")
def test_login_user_not_exist(page: Page, test_report_file: str):
    login_page = Auth.LOGIN
    page.goto(login_page)

    page.fill("input[type='text'][name='username']", "usernotexist")
    page.fill("input[type='password'][name='password']", "usernotexist")
    with page.expect_response("**/auth/login") as resp_info:
        page.click("button[type='submit']")

    response = resp_info.value

    actual_status = response.status
    return [
        (Message.STATUS, 404, actual_status)
    ]
