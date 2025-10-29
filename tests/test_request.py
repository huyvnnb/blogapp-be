from playwright.sync_api import Page, APIRequestContext

from tests.pages import HomePage
from tests.test_user_auth import _login

# base_url = "http://localhost:3000"


def test_logout(page: Page, api_request: APIRequestContext, test_factory, base_data):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    response = _login(page, payload={'username': user.username, 'password': password})
    data = response.json().get('data')
    if data is not None:
        revoked_token = data.get('token')
    else:
        revoked_token = None

    home_page = HomePage(page)
    home_page.menu_option.click()
    home_page.logout()

    response = api_request.get(
        "/users/me",
        headers={"Authorization": f"Bearer {revoked_token}"}
    )
    print(f"Response: {response}")

    assert response.status == 401, f"Expect 401, got {response.status}"


def test_user_approve_post(page, api_request, test_factory, base_data):
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

    assert response.status == 403
