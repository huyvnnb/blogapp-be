import random
import time
import uuid

from playwright.sync_api import Page, expect, Locator

from blog.posts import Posts
from tests.endpoints import Post
from tests.messages import Message
from tests.pages import HomePage, EditorPage
from tests.test_user_auth import _login
from tests.testcase_helper import log_test_result
import logging
import pytest_check as check


logger = logging.getLogger()


@log_test_result(test_case_ids="TC3.1")
def test_create_post_check_status_code(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    _login(page, payload={'username': user.username, 'password': password})

    editor_page = EditorPage(page)

    page.goto(Post.NEW_POST)

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    editor_page.fill_title(title)
    editor_page.fill_summary(summary)
    editor_page.fill_content(content)

    editor_page.select_dropdown_option(0, "Public")
    response = editor_page.publish()

    return [
        (Message.STATUS, 201, str(response.status)),
    ]


@log_test_result(test_case_ids="TC3.2")
def test_create_post_check_existence(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    editor_page = EditorPage(page)

    page.goto(Post.NEW_POST)

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    editor_page.fill_title(title)
    editor_page.fill_summary(summary)
    editor_page.fill_content(content)

    editor_page.select_dropdown_option(0, "Public")
    editor_page.publish()

    post_item = home_page.post_item_by_article(title)
    post_title = home_page.post_title(post_item)
    post_status = home_page.badge(post_item, 0)

    expected = {
        "post": {
            "title": title,
            "status": "Pending"
        }
    }

    actual = {
        "post": {
            "title": post_title,
            "status": post_status
        }
    }

    return [
        (Message.POST_INFO, expected, actual)
    ]


@log_test_result("TC3.3")
def test_create_post_check_validation(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    _login(page, payload={'username': user.username, 'password': password})

    editor_page = EditorPage(page)

    page.goto(Post.NEW_POST)

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = ""

    editor_page.fill_title(title)
    editor_page.fill_summary(summary)
    editor_page.fill_content(content)

    editor_page.select_dropdown_option(0, "Public")
    response = editor_page.publish()

    return [
        (Message.STATUS, 422, str(response.status))
    ]


@log_test_result("TC4.1")
def test_update_public_to_private(page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    edit_page = EditorPage(page)

    compare_value = []
    post_item = home_page.post_item_by_article(title)
    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.select_dropdown_option(0, "Private")

    response = edit_page.update()

    post_public = home_page.badge(post_item, 0)

    compare_value.extend(
        [
            (Message.STATUS, 200, response.status),
        ]
    )
    return compare_value


@log_test_result("TC4.2")
def test_update_public_to_private_check_status(page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    edit_page = EditorPage(page)

    post_item = home_page.post_item_by_article(title)
    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.select_dropdown_option(0, "Private")
    edit_page.update()

    post_public = home_page.badge(post_item, 0)

    expected = {
        "status": "Private"
    }
    actual = {
        "status": post_public
    }

    compare_value = [(Message.POST_BADGE_PUBLIC, expected, actual)]
    return compare_value


@log_test_result("TC4.3")
def test_update_publish_to_draft(page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    edit_page = EditorPage(page)

    compare_value = []
    post_item = home_page.post_item_by_article(title)

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.select_dropdown_option(1, "Draft")

    response = edit_page.update()

    compare_value.extend(
        [
            (Message.STATUS, 200, response.status),
        ]
    )
    return compare_value


@log_test_result("TC4.4")
def test_update_publish_to_draft_check_status(page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    edit_page = EditorPage(page)

    post_item = home_page.post_item_by_article(title)

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.select_dropdown_option(1, "Draft")
    edit_page.update()

    post_publish = home_page.badge(post_item, 1)

    expected = {"status": "Draft"}
    actual = {"status": post_publish}

    compare_value = [(Message.POST_BADGE_PUBLIC, expected, actual)]
    return compare_value


@log_test_result("TC5.1")
def test_update_title_check_status_code(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    edit_page = EditorPage(page)

    compare_values = []

    post_item = home_page.post_item_by_article(title)

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.content_input.wait_for(timeout=1000)
    new_title = f"{title} {int(time.time())}"
    edit_page.fill_title(new_title)

    response = edit_page.update()

    compare_values.extend([
        (Message.STATUS, 200, str(response.status)),
    ])

    return compare_values


@log_test_result("TC5.2")
def test_update_title_check_post_status(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    edit_page = EditorPage(page)

    post_item = home_page.post_item_by_article(title)

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    # edit_page.content_input.wait_for(timeout=1000)
    page.wait_for_load_state("networkidle")
    expect(edit_page.title_input).not_to_be_empty()
    new_title = f"{title} - updated"
    edit_page.fill_title(new_title)
    edit_page.update()

    post_item = home_page.post_item_by_article(new_title)
    post_title = home_page.post_title(post_item)
    badge = home_page.badge(post_item, 0)
    expected = {
        "posts": {
            "title": new_title,
            "status": "Pending"
        }
    }

    actual = {
        "posts": {
            "title": post_title,
            "status": badge
        }
    }
    compare_values = [
        (Message.POST_INFO, expected, actual)
    ]

    return compare_values


@log_test_result(test_case_ids="TC6.1")
def test_delete_post_check_status_code(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(title)
    delete_btn = home_page.delete_btn(post_item)

    with page.expect_response(lambda r: "/posts" in r.url) as resp_info:
        page.once("dialog", lambda dialog: dialog.accept())
        delete_btn.click()

    response = resp_info.value

    return [
        (Message.STATUS, 200, response.status),
    ]


@log_test_result(test_case_ids="TC6.2")
def test_delete_post_check_existence(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Title of post - {int(time.time())}"
    summary = "Summary of post"
    content = "Content of post"

    test_factory.create_post(
        user,
        title=title,
        summary=summary,
        content=content,
        status="APPROVE",
        published=True,
        is_public=True
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(title)
    delete_btn = home_page.delete_btn(post_item)

    with page.expect_response(lambda r: "/posts" in r.url):
        page.once("dialog", lambda dialog: dialog.accept())
        delete_btn.click()

    def check_post_not_visible(timeout=3000):
        try:
            expect(post_item).not_to_be_visible(timeout=timeout)
            return False
        except TimeoutError:
            return True
        except Exception as e:
            return Message.ERROR.format(error=str(e))

    visible = check_post_not_visible()
    actual_value = post_item if visible else "-"
    return [
        (Message.POST_VISIBILITY, "-", actual_value)
    ]
