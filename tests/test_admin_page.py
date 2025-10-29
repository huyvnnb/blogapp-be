from playwright.sync_api import Page, expect

from tests.endpoints import Admin
from tests.pages import AdminPage, HomePage
from tests.test_user_auth import _login


def _admin_login(page: Page, payload: dict):
    page.goto(Admin.LOGIN)
    page.locator("input[name='username']").fill(payload["username"])
    page.locator("input[name='password']").fill(payload["password"])

    with page.expect_response("**/admin/login") as resp_info:
        page.locator("button[type='submit']").click()

    return resp_info


def test_admin_login(page: Page, test_factory, base_data):
    admin, password = test_factory.create_user(base_data["role_ids"]["admin"])

    resp_infp = _admin_login(page, payload={"username": admin.username, "password": password})

    response = resp_infp.value

    assert response.status == 200
    # page.get_by_test_id("admin-username").fill(admin.username)
    # page.get_by_test_id("admin-password").fill("password")
    # with page.expect_response("**/admin/login") as resp_info:
    #     page.get_by_test_id("admin-login-btn").click()
    # response = resp_info.value
    #
    # assert response.status == 200


def test_user_login_admin(page: Page, db_session, base_data, test_factory):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    resp_info = _admin_login(page, payload={"username": user.username, "password": password})

    response = resp_info.value
    assert response.status == 403


def test_pending_list(page: Page, test_factory, base_data):
    user, user_pw = test_factory.create_user(base_data["role_ids"]["user"])
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])

    approve_count = 5
    pending_count = 5
    reject_count = 5

    test_factory.create_posts(
        user,
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
        status="APPROVE",
        count=approve_count
    )

    pending_posts = test_factory.create_posts(
        user,
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
        status="PENDING",
        count=pending_count
    )

    test_factory.create_posts(
        user,
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
        status="REJECT",
        count=reject_count
    )

    _admin_login(page, payload={"username": admin.username, "password": admin_pw})

    page.goto(Admin.POST_MANAGE)
    admin_page = AdminPage(page)

    pending_list = admin_page.pending_list
    expect(pending_list).to_have_count(pending_count)

    expect_title = {post.title for post in pending_posts}
    count = pending_list.count()

    actual_title = {
        admin_page.pending_title(pending_list.nth(i))
        for i in range(count)
    }

    assert expect_title == actual_title


def test_approve_post(page: Page, test_factory, base_data):
    user, user_pw = test_factory.create_user(base_data["role_ids"]["user"])
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])

    pending_post = test_factory.create_post(
        user,
        status="PENDING"
    )

    _admin_login(page, payload={"username": admin.username, "password": admin_pw})
    page.goto(Admin.POST_MANAGE)
    admin_page = AdminPage(page)

    pending_item = admin_page.pending_item(pending_post.title)

    with page.expect_response("**/status") as resp_info:
        admin_page.approve(pending_item)

    response = resp_info.value
    assert response.status == 200

    page.goto(Admin.HOME)
    admin_page.logout()

    page.wait_for_load_state("networkidle")
    _login(page, payload={'username': user.username, 'password': user_pw})

    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(pending_post.title)
    assert home_page.post_title(post_item) == pending_post.title
    assert home_page.badge(post_item, 0) == "Approved"


def test_reject_post(page: Page, test_factory, base_data):
    user, user_pw = test_factory.create_user(base_data["role_ids"]["user"])
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])

    pending_post = test_factory.create_post(
        user,
        status="PENDING"
    )

    _admin_login(page, payload={"username": admin.username, "password": admin_pw})
    page.goto(Admin.POST_MANAGE)
    admin_page = AdminPage(page)

    pending_item = admin_page.pending_item(pending_post.title)

    with page.expect_response("**/status") as resp_info:
        admin_page.reject(pending_item)

    response = resp_info.value
    assert response.status == 200

    page.goto(Admin.HOME)
    logout_btn = admin_page.logout_btn
    logout_btn.highlight()
    logout_btn.click()

    page.wait_for_load_state("networkidle")
    _login(page, payload={'username': user.username, 'password': user_pw})

    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(pending_post.title)
    assert home_page.post_title(post_item) == pending_post.title
    assert home_page.badge(post_item, 0) == "Rejected"
