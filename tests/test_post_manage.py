import random
import time
import uuid

from playwright.sync_api import Page, expect, Locator

from blog.posts import Posts
from tests.endpoints import Post
from tests.pages import HomePage, EditorPage
from tests.test_user_auth import _login


def test_create_post(page: Page, test_factory, base_data):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    editor_page = EditorPage(page)

    page.goto(Post.NEW_POST)

    title = f"Blockchain IoT - {int(time.time())}"
    summary = "Blockchain đang mở ra hướng mới..."
    content = """
    ## Blockchain là gì?
    ...
    """

    editor_page.fill_title(title)
    editor_page.fill_summary(summary)
    editor_page.fill_content(content)

    editor_page.select_dropdown_option(0, "Public")
    response = editor_page.publish()

    assert response.status == 201, f"Unexpected status: {response.status}"

    post_item = home_page.post_item_by_article(title)
    assert home_page.post_title(post_item) == title
    assert home_page.badge(post_item, 0) == "Pending"
    assert home_page.badge(post_item, 1) == "Public"
    assert home_page.badge(post_item, 2) == "Published"


def test_update_public_to_private(page, test_factory, base_data):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Blockchain IoT - {int(time.time())}"
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
    assert home_page.badge(post_item, 0) == "Approved"
    assert home_page.badge(post_item, 1) == "Public"
    assert home_page.badge(post_item, 2) == "Published"

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.select_dropdown_option(0, "Private")
    edit_page.select_dropdown_option(1, "Draft")

    response = edit_page.update()

    assert response.status == 200

    assert home_page.post_title(post_item) == title
    assert home_page.badge(post_item, 0) == "Private"
    assert home_page.badge(post_item, 1) == "Draft"


def test_update_content(page: Page, test_factory, base_data):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Blockchain IoT - {int(time.time())}"
    summary = "..."
    content = "..."

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
    assert home_page.badge(post_item, 0) == "Approved"

    edit_btn = home_page.edit_btn(post_item)
    edit_btn.click()

    edit_page.content_input.wait_for(timeout=1000)
    new_content = f"{content} {int(time.time())}"
    edit_page.fill_content(new_content)

    expect(edit_page.content_input).to_have_value(new_content, timeout=2000)

    response = edit_page.update()
    assert response.status == 200

    assert home_page.badge(post_item, 0) == "Pending"


def test_delete_post(page: Page, test_factory, base_data):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    title = f"Blockchain IoT - {int(time.time())}"
    summary = "..."
    content = "..."

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
    assert response.status == 200

    expect(post_item).not_to_be_visible(timeout=5000)


def test_check_post_number(page, base_data, test_factory):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    post_num = 10
    status = ["APPROVE", "PENDING", "REJECT"]
    is_public = [True, False]
    published = [True, False]

    expected_posts = []
    for i in range(post_num):
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

    home_page = HomePage(page)
    posts_item = home_page.all_post_items()
    expect(posts_item).to_have_count(post_num)

    status_mapping = {
        "approve": "Approved",
        "pending": "Pending",
        "reject": "Rejected"
    }

    for post in expected_posts:
        item = posts_item.filter(has_text=post.title)

        assert home_page.post_title(item) == post.title
        badge_idx = 0
        if post.is_public and post.published:
            assert home_page.badge(item, badge_idx) == status_mapping[post.status.value]
            badge_idx += 1
        assert home_page.badge(item, badge_idx) == "Public" if post.is_public else "Private"
        badge_idx += 1
        assert home_page.badge(item, badge_idx) == "Published" if post.published else "Draft"


def test_search_feature(page: Page, base_data, test_factory):
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

    expect(posts).to_have_count(visible_posts)

    for post in expected_posts:
        # print(f"{post.title}: {page.locator("p.font-medium", has_text=f"{post.title}").count()}")
        post_item = home_page.post_search_with_title(post.title)
        post_item.highlight()

        assert home_page.post_search_title(post_item) == post.title
        assert home_page.post_search_author(post_item) == post.user.username

