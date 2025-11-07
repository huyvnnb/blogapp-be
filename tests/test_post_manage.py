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


@log_test_result(test_case_ids="TC4")
def test_create_post(page: Page, test_factory, base_data, test_report_file):
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
    response = editor_page.publish()

    post_item = home_page.post_item_by_article(title)
    post_title = home_page.post_title(post_item)
    post_status = home_page.badge(post_item, 0)
    # post_public = home_page.badge(post_item, 1)
    # post_publish = home_page.badge(post_item, 2)

    return [
        (Message.STATUS, 201, str(response.status)),
        (Message.SEP.format(content=""), "", ""),
        (Message.POST_TITLE, title, post_title),
        (Message.BADGE_APPROVE, "Pending", post_status),
        # (Message.BADGE_PUBLIC, "Public", post_public),
        # (Message.BADGE_PUBLISH, "Published", post_publish)
    ]


@log_test_result("TC5")
def test_create_post_validation(page: Page, test_factory, base_data, test_report_file):
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


@log_test_result("TC6")
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
    # post_status = home_page.badge(post_item, 0)
    # post_public = home_page.badge(post_item, 1)
    # post_publish = home_page.badge(post_item, 2)
    # compare_value.extend(
    #     [
    #         (Message.PRE_BADGE_APPROVE, "Approved", post_status),
    #         (Message.PRE_BADGE_PUBLIC, "Public", post_public),
    #         (Message.PRE_BADGE_PUBLISH, "Published", post_publish)
    #     ]
    # )

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.select_dropdown_option(0, "Private")
    # edit_page.select_dropdown_option(1, "Draft")

    response = edit_page.update()

    post_public = home_page.badge(post_item, 0)

    compare_value.extend(
        [
            (Message.STATUS, 200, response.status),
            (Message.POST_BADGE_PUBLIC, "Private", post_public)
        ]
    )
    return compare_value


@log_test_result("TC7")
def test_update_content(page: Page, test_factory, base_data, test_report_file):
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
    # post_status = home_page.badge(post_item, 0)
    # compare_values.extend([
    #     (Message.PRE_BADGE_APPROVE, "Approved", post_status)
    # ])

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.content_input.wait_for(timeout=1000)
    new_title = f"{title} {int(time.time())}"
    edit_page.fill_title(new_title)

    response = edit_page.update()

    post_title = home_page.post_title(post_item)
    badge = home_page.badge(post_item, 0)
    compare_values.extend([
        (Message.STATUS, 200, str(response.status)),
        (Message.POST_TITLE, new_title, post_title),
        (Message.POST_BADGE_APPROVE, "Pending", badge)
    ])

    return compare_values


@log_test_result(test_case_ids="TC8")
def test_delete_post(page: Page, test_factory, base_data, test_report_file):
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
        (Message.STATUS, 200, response.status),
        (Message.POST_VISIBILITY, "-", actual_value)
    ]


@log_test_result("TC9")
def test_check_post_number(page: Page, base_data, test_factory, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    post_num = 3
    status = ["APPROVE", "PENDING", "REJECT"]
    is_public = [True, False]
    published = [True, False]

    expected_posts = []
    for _ in range(post_num):
        uid = str(uuid.uuid4())[:8]
        title = f"Title - {uid}"
        summary = f"Summary - {uid}"
        content = f"Content - {uid}"
        status_choice = random.choice(status)

        if status_choice == "PENDING":
            public = random.choice(is_public)
            publish = random.choice(published)
        else:
            public = True
            publish = True
        post = test_factory.create_post(
            user,
            title=title,
            summary=summary,
            content=content,
            status=status_choice,
            published=publish,
            is_public=public
        )
        expected_posts.append(post)

    _login(page, payload={'username': user.username, 'password': password})

    compare_values = []
    home_page = HomePage(page)

    page.wait_for_load_state("networkidle")
    posts_item = home_page.all_post_items()
    compare_values.append(
        (Message.POST_COUNT, post_num, posts_item.count())
    )

    status_mapping = {
        "approve": "Approved",
        "pending": "Pending",
        "reject": "Rejected"
    }

    for post in expected_posts:
        actual_value = []
        expect_value = []
        item = posts_item.filter(has_text=post.title)
        post_title = home_page.post_title(item)
        actual_value.append(post_title)
        expect_value.append(post.title)
        badge_idx = 0

        if post.is_public and post.published:
            expect_status = status_mapping[post.status.value]
            actual_status = home_page.badge(item, badge_idx)
            actual_value.append(actual_status)
            expect_value.append(expect_status)
            badge_idx += 1

        expect_public = "Public" if post.is_public else "Private"
        actual_public = home_page.badge(item, badge_idx)
        badge_idx += 1

        expect_publish = "Published" if post.published else "Draft"
        actual_publish = home_page.badge(item, badge_idx)

        actual_value.extend([actual_public, actual_publish])
        expect_value.extend([expect_public, expect_publish])

        compare_values.append((Message.POST_INFO, expect_value, actual_value))

    return compare_values


@log_test_result("TC10")
def test_search_feature(page: Page, base_data, test_factory, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    visible_posts = 15
    invisible_posts = 10

    expected_posts = test_factory.create_posts(
        user,
        title_pref="K8s",
        summary="K8s",
        content="k8s",
        count=visible_posts
    )

    test_factory.create_posts(
        user,
        title_pref="K8s",
        summary="K8s",
        content="K8s",
        status="PENDING",
        count=invisible_posts
    )

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    search_bar = home_page.search_bar
    search_bar.click()

    search_topic = "k8s"
    home_page.search_field.fill(search_topic)

    result_field = home_page.result_field

    posts = home_page.all_posts
    if visible_posts > 10:
        last_height = 0
        while True:
            result_field.evaluate("(el) => el.scrollTo(0, el.scrollHeight)")
            page.wait_for_timeout(800)

            new_height = result_field.evaluate("(el) => el.scrollHeight")
            if last_height == new_height:
                break

            last_height = new_height

    # expect(posts).to_have_count(visible_posts)
    compare_values = [(Message.POST_SEARCH_COUNT, visible_posts, posts.count())]

    for post in expected_posts:
        post_item = home_page.post_search_with_title(post.title)
        post_item.highlight()

        post_title = home_page.post_search_title(post_item)
        post_author = home_page.post_search_author(post_item)

        compare_values.append(
            (Message.POST_INFO, [post.title, post.user.username], [post_title, post_author])
        )

        # compare_values.extend([
        #     (Message.POST_TITLE, post.title, post_title),
        #     (Message.POST_AUTHOR, post.user.username, post_author)
        # ])
        # assert home_page.post_search_title(post_item) == post.title
        # assert home_page.post_search_author(post_item) == post.user.username
    return compare_values

