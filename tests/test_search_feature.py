from playwright.sync_api import Page

from tests.messages import Message
from tests.pages import HomePage
from tests.test_user_auth import _login
from tests.testcase_helper import log_test_result


@log_test_result("TC7.1")
def test_search_feature_check_count(page: Page, base_data, test_factory, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    visible_posts = 15
    invisible_posts = 10

    test_factory.create_posts(
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

    compare_values = [(Message.POST_SEARCH_COUNT, visible_posts, posts.count())]

    return compare_values


@log_test_result("TC7.2")
def test_search_feature_check_detail(page: Page, base_data, test_factory, test_report_file):
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

    if visible_posts > 10:
        last_height = 0
        while True:
            result_field.evaluate("(el) => el.scrollTo(0, el.scrollHeight)")
            page.wait_for_timeout(800)

            new_height = result_field.evaluate("(el) => el.scrollHeight")
            if last_height == new_height:
                break

            last_height = new_height

    expected = {"posts": []}
    actual = {"posts": []}

    for post in expected_posts:
        post_item = home_page.post_search_with_title(post.title)
        post_item.highlight()

        post_title = home_page.post_search_title(post_item)
        post_author = home_page.post_search_author(post_item)

        expected["posts"].append(
            {"title": post.title, "author": post.user.username}
        )
        actual["posts"].append(
            {"title": post_title, "author": post_author}
        )

    return [
        (Message.POST_INFO, expected, actual)
    ]


@log_test_result("TC7.3")
def test_search_feature_check_no_post(page: Page, base_data, test_factory, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    visible_posts = 15
    invisible_posts = 10

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

    if visible_posts > 10:
        last_height = 0
        while True:
            result_field.evaluate("(el) => el.scrollTo(0, el.scrollHeight)")
            page.wait_for_timeout(800)

            new_height = result_field.evaluate("(el) => el.scrollHeight")
            if last_height == new_height:
                break

            last_height = new_height

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

    compare_values = [(Message.POST_SEARCH_COUNT, 0, posts.count())]

    return compare_values


