import random
import uuid
from collections import defaultdict

from playwright.sync_api import Page

from tests.messages import Message
from tests.pages import HomePage
from tests.test_user_auth import _login
from tests.testcase_helper import log_test_result


@log_test_result("TC4.5")
def test_check_post_number_count(page: Page, base_data, test_factory, test_report_file):
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

    return compare_values


@log_test_result("TC4.6")
def test_check_user_post_detail(page: Page, base_data, test_factory, test_report_file):
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

    status_mapping = {
        "approve": "Approved",
        "pending": "Pending",
        "reject": "Rejected"
    }

    expected = {"posts": []}
    actual = {"posts": []}

    for post in expected_posts:
        expected_status = None
        if post.is_public and post.published:
            expected_status = status_mapping[post.status.value]

        expected["posts"].append({
            "title": post.title,
            "status": expected_status,
            "public": "Public" if post.is_public else "Private",
            "publish": "Published" if post.published else "Draft"
        })

        item = posts_item.filter(has_text=post.title)
        post_title = home_page.post_title(item)
        badge_idx = 0
        actual_status = None

        if post.is_public and post.published:
            actual_status = home_page.badge(item, badge_idx)
            badge_idx += 1

        actual_public = home_page.badge(item, badge_idx)
        badge_idx += 1
        actual_publish = home_page.badge(item, badge_idx)

        actual["posts"].append({
            "title": post_title,
            "status": actual_status,
            "public": actual_public,
            "publish": actual_publish
        })

    compare_values.append((Message.POST_INFO, expected, actual))

    return compare_values



