from playwright.sync_api import Page, expect

from tests.endpoints import Admin
from tests.messages import Message, PostManageMsg
from tests.pages import AdminPage, HomePage
from tests.test_user_auth import _login
from tests.testcase_helper import log_test_result, compare_set


def _admin_login(page: Page, payload: dict):
    page.goto(Admin.LOGIN)
    page.locator("input[name='username']").fill(payload["username"])
    page.locator("input[name='password']").fill(payload["password"])

    with page.expect_response("**/admin/login") as resp_info:
        page.locator("button[type='submit']").click()

    return resp_info


@log_test_result(test_case_ids="TC9.1")
def test_admin_login(page: Page, test_factory, base_data, test_report_file):
    admin, password = test_factory.create_user(base_data["role_ids"]["admin"])

    resp_infp = _admin_login(page, payload={"username": admin.username, "password": password})

    response = resp_infp.value

    return [
        (Message.STATUS, 200, response.status)
    ]


@log_test_result(test_case_ids="TC9.2")
def test_user_login_admin(page: Page, db_session, base_data, test_factory, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    resp_info = _admin_login(page, payload={"username": user.username, "password": password})

    response = resp_info.value

    return [
        (Message.STATUS, 403, response.status)
    ]


@log_test_result(test_case_ids="TC10.1")
def test_pending_list(page: Page, test_factory, base_data, test_report_file):
    user, _ = test_factory.create_user(base_data["role_ids"]["user"])
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])

    approve_count = 2
    pending_count = 2
    reject_count = 2

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
        title_pref="Pending post",
        summary="Pending summary",
        content="Pending content",
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
    page.wait_for_load_state("networkidle")
    admin_page = AdminPage(page)

    compare_values = []

    pending_list = admin_page.pending_list
    actual_count = pending_list.count()
    expected = {"total": pending_count, "posts": []}
    actual = {"total": actual_count, "posts": []}
    # compare_values.append(
    #     (PostManageMsg.PENDING_LIST_COUNT, pending_count, actual_count)
    # )

    for post in pending_posts:
        expected["posts"].append(post.title)

    for i in range(actual_count):
        actual["posts"].append(admin_page.pending_title(pending_list.nth(i)))

    # expect_title = {post.title for post in pending_posts}
    # count = pending_list.count()
    #
    # actual_title = {
    #     admin_page.pending_title(pending_list.nth(i))
    #     for i in range(count)
    # }

    # values = compare_set(expect_title, actual_title)
    # for value in values:
    #     expect_item, actual_item = value
    #     compare_values.append(
    #         (PostManageMsg.POST_TITLE, expect_item, actual_item)
    #     )

    return [
        ("", expected, actual)
    ]


@log_test_result(test_case_ids="TC10.2")
def test_approve_post_check_status_code(page: Page, test_factory, base_data, test_report_file):
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
    compare_values = [(Message.STATUS, 200, response.status)]

    return compare_values


@log_test_result(test_case_ids="TC10.3")
def test_approve_post_check_display(page: Page, test_factory, base_data, test_report_file):
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

    with page.expect_response("**/status"):
        admin_page.approve(pending_item)

    page.goto(Admin.HOME)
    admin_page.logout()

    page.wait_for_load_state("networkidle")
    _login(page, payload={'username': user.username, 'password': user_pw})

    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(pending_post.title)

    expected = {"status": "Approved"}
    actual = {"status": home_page.badge(post_item, 0)}
    # compare_values.append(
    #     (Message.BADGE_APPROVE, "Approved", home_page.badge(post_item, 0))
    # )

    return [
        (Message.BADGE_APPROVE, expected, actual)
    ]


@log_test_result(test_case_ids="TC10.4")
def test_reject_post_check_status_code(page: Page, test_factory, base_data, test_report_file):
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
    compare_values = [(Message.STATUS, 200, response.status)]

    return compare_values


@log_test_result(test_case_ids="TC10.5")
def test_reject_post_check_display(page: Page, test_factory, base_data, test_report_file):
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

    with page.expect_response("**/status"):
        admin_page.reject(pending_item)

    compare_values = []

    page.goto(Admin.HOME)
    logout_btn = admin_page.logout_btn
    logout_btn.click()

    page.wait_for_load_state("networkidle")
    _login(page, payload={'username': user.username, 'password': user_pw})

    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(pending_post.title)
    expected = {"status": "Rejected"}
    actual = {"status": home_page.badge(post_item, 0)}
    # compare_values.append(
    #     (Message.BADGE_APPROVE, "Rejected", home_page.badge(post_item, 0))
    # )
    return [(Message.BADGE_APPROVE, expected, actual)]
