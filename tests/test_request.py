import pytest
from playwright.sync_api import Page, APIRequestContext

from tests.messages import Message
from tests.pages import HomePage
from tests.test_user_auth import _login
from tests.testcase_helper import log_test_result


@log_test_result(test_case_ids="TC3")
def test_logout(page: Page, api_request: APIRequestContext, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    response = _login(page, payload={'username': user.username, 'password': password})
    data = response.json().get('data')
    if data is not None:
        revoked_token = data.get('token')
    else:
        revoked_token = None

    home_page = HomePage(page)
    home_page.menu_option.wait_for(state="visible", timeout=5000)
    home_page.menu_option.click()
    home_page.logout()
    import time
    time.sleep(1)

    response = api_request.get(
        "/users/me",
        headers={"Authorization": f"Bearer {revoked_token}"}
    )
    actual_status = response.status

    return [
        (Message.STATUS, 401, actual_status)
    ]


@log_test_result(test_case_ids="TC18")
def test_user_approve_post(page, api_request, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    post = test_factory.create_post(
        user,
        status="PENDING"
    )
    response = _login(page, payload={'username': user.username, 'password': password})
    data = response.json().get('data')
    if data is not None:
        revoked_token = data.get('token')
    else:
        revoked_token = None

    response = api_request.patch(
        f"/admin/posts/{post.id}/status",
        data={"status": "APPROVE"},
        headers={"Authorization": f"Bearer {revoked_token}"}
    )

    return [
        (Message.STATUS, 403, response.status)
    ]
