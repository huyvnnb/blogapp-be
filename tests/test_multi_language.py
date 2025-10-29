import json
from pathlib import Path

import pytest
import unicodedata
from playwright.sync_api import Page, expect

from tests.endpoints import Post, Auth, Dashboard, Admin
from tests.pages import HomePage, norm, EditorPage, DashboardPage, AdminPage
from tests.test_admin_page import _admin_login
from tests.test_user_auth import _login


def load_lang(lang: str):
    print(f"Loading lang: {lang}")
    base_dir = Path(__file__).parent / "langs"
    with open(base_dir / f"{lang}.json", encoding="utf-8") as f:
        data = json.load(f)

    # def normalize_dict(d):
    #     for k, v in d.items():
    #         if isinstance(v, dict):
    #             normalize_dict(v)
    #         elif isinstance(v, str):
    #             d[k] = unicodedata.normalize("NFC", v)
    #
    # normalize_dict(data)
    return data


@pytest.fixture(scope="session", params=["vi", "en"])
def lang(request):
    return request.param


@pytest.fixture(scope="session")
def lang_map(lang):
    return load_lang(lang)


def assert_text_equal(actual: str, expected: str):
    import unicodedata
    a = unicodedata.normalize("NFC", actual.strip())
    e = unicodedata.normalize("NFC", expected.strip())
    assert a == e, f"Expected '{e}', got '{a}'"


def test_ml_bar(page: Page, test_factory, base_data, lang, lang_map):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    home_page.choose_lang(lang)
    navbar = lang_map["navbar"]
    sidebar = lang_map["sidebar"]

    assert_text_equal(home_page.menu_posts, navbar["posts"])
    assert_text_equal(home_page.menu_explore, navbar["explore"])
    assert_text_equal(home_page.sidebar_home, sidebar["home"])
    assert_text_equal(home_page.sidebar_new_post, sidebar["new_post"])
    assert_text_equal(home_page.sidebar_dashboard, sidebar["dashboard"])


def test_ml_home(page: Page, test_factory, base_data, lang, lang_map):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    test_factory.create_post(user)
    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    home_page.choose_lang(lang)
    home = lang_map["home"]

    assert_text_equal(home_page.new_post, home["new_post"])
    assert_text_equal(home_page.page_title, home["posts"])


def test_ml_edit_page(page, test_factory, base_data, lang, lang_map):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    post = test_factory.create_post(user)
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Post.NEW_POST)

    editor_page = EditorPage(page)
    editor_page.choose_lang(lang)
    edit = lang_map["edit_page"]

    assert_text_equal(editor_page.publish_btn_text, edit["publish"])
    assert_text_equal(editor_page.draft_btn_text, edit["draft"])
    assert_text_equal(editor_page.title_placeholder, edit["title_placeholder"])
    assert_text_equal(editor_page.summary_placeholder, edit["summary_placeholder"])
    assert_text_equal(editor_page.content_placeholder, edit["content_placeholder"])

    page.goto(Auth.HOME)
    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(post.title)
    home_page.edit_btn(post_item).click()

    assert_text_equal(editor_page.update_btn_text, edit["update"])


def test_ml_user_dashboard(page, test_factory, base_data, lang, lang_map):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard = lang_map["dashboard_page"]

    assert_text_equal(dashboard_page.dashboard_title, dashboard["user_dashboard_title"])
    assert_text_equal(dashboard_page.dashboard_desc, dashboard["user_dashboard_desc"])

    assert_text_equal(dashboard_page.approved_card_text, dashboard["approved"])
    assert_text_equal(dashboard_page.pending_card_text, dashboard["pending"])
    assert_text_equal(dashboard_page.rejected_card_text, dashboard["rejected"])
    assert_text_equal(dashboard_page.total_card_text, dashboard["total"])

    assert_text_equal(dashboard_page.activity_text, dashboard["activity"])

    expected_month = lang_map["month"].values()
    actual_month = dashboard_page.month_text_list
    for i in range(len(expected_month)):
        assert_text_equal(actual_month[i], actual_month[i])


def test_ml_export_dialog(page, test_factory, base_data, lang, lang_map):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard_page.export_btn.click()

    dialog_key = lang_map["export_dialog_key"]
    dialog_map = lang_map["export_dialog"]
    keys = dialog_key.keys()

    assert_text_equal(dashboard_page.select_all_btn_text, dialog_map["select_all"])
    dashboard_page.select_all_btn.click()
    assert_text_equal(dashboard_page.select_all_btn_text, dialog_map["deselect_all"])

    assert_text_equal(dashboard_page.select_all_post_fields_text, dialog_map["select_all"])
    dashboard_page.select_all_post_fields.click()
    assert_text_equal(dashboard_page.select_all_post_fields_text, dialog_map["deselect_all"])

    for key in keys:
        assert_text_equal(dashboard_page.label_text(key), dialog_key[key])

    assert_text_equal(dashboard_page.dialog_cancel_btn_text, dialog_map["cancel"])
    assert_text_equal(dashboard_page.dialog_export_btn_text, dialog_map["export"])


def test_ml_admin_home(page, test_factory, base_data, lang, lang_map):
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])
    _admin_login(page, payload={"username": admin.username, "password": admin_pw})

    admin_page = AdminPage(page)
    admin_page.choose_lang(lang)

    home = lang_map["admin"]["home"]

    assert_text_equal(admin_page.logout_btn_text, home["logout"])
    assert_text_equal(admin_page.post_manage_card_title, home["post_manage"])
    assert_text_equal(admin_page.post_manage_card_desc, home["post_manage_desc"])
    assert_text_equal(admin_page.home_title, home["admin_dashboard"])
    assert_text_equal(admin_page.post_manage_card_btn_text, home["access"])
    assert_text_equal(admin_page.home_text, home["home"])
    assert_text_equal(admin_page.post_management_text, home["post_manage"])


def test_ml_admin_post_manage(page, test_factory, base_data, lang, lang_map):
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    test_factory.create_post(
        user,
        status="PENDING"
    )
    _admin_login(page, payload={"username": admin.username, "password": admin_pw})

    page.goto(Admin.POST_MANAGE)
    admin_page = AdminPage(page)
    admin_page.choose_lang(lang)
    posts = lang_map["admin"]["posts"]

    assert_text_equal(admin_page.post_stats_card_title, posts["statistics"])
    assert_text_equal(admin_page.post_ratio_card_title, posts["post_ratio"])
    assert_text_equal(admin_page.post_pending_card_title, posts["pending_title"])

    expect_header = [posts["title"], posts["author"], posts["created"], posts["status"], posts["action"]]
    actual_header = admin_page.table_header_list

    for i in range(len(expect_header)):
        assert_text_equal(actual_header[i], expect_header[i])

    expect_ratio_attributes = [posts["approve"], posts["pending"], posts["reject"]]
    actual_ratio_attributes = admin_page.post_ratio_attribute

    for i in range(len(expect_ratio_attributes)):
        assert_text_equal(expect_ratio_attributes[i], actual_ratio_attributes[i])

    time_range = lang_map["range"]
    expect_case = [list(time_range[k].values()) for k in ["daily", "weekly", "monthly", "yearly"]]

    for i in range(4):
        admin_page.dropdown_menu(0).click()
        admin_page.dropdown_option.nth(i).click()
        admin_page.dropdown_menu(1).click()

        case = expect_case[i]
        actual = admin_page.dropdown_option_list

        print(f"Case: {case}")
        print(f"Actual: {actual}")
        for j in range(len(case)):
            assert_text_equal(actual[j], case[j])

        admin_page.page.keyboard.press("Escape")
        # admin_page.page.wait_for_selector("[data-state='open']", state="detached")

    admin_page.dropdown_menu(2).click()
    post_status_list = admin_page.dropdown_option_list
    assert post_status_list == [posts["approve"], posts["reject"]]

