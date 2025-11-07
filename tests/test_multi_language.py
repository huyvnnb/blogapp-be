import json
from itertools import zip_longest
from pathlib import Path

import pytest
from playwright.sync_api import Page

from tests.endpoints import Post, Auth, Dashboard, Admin
from tests.messages import NavbarMsg, HomeMsg, EditMsg, DashboardMsg, DialogMsg, AdminHomeMsg, PostManageMsg
from tests.pages import HomePage, EditorPage, DashboardPage, AdminPage
from tests.test_admin_page import _admin_login
from tests.test_user_auth import _login
from tests.testcase_helper import log_test_result
import logging

logger = logging.getLogger()


def load_lang(lang: str):
    print(f"Loading lang: {lang}")
    base_dir = Path(__file__).parent / "langs"
    with open(base_dir / f"{lang}.json", encoding="utf-8") as f:
        data = json.load(f)

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


@log_test_result(test_case_ids=["TC19", "TC20"])
def test_ml_bar(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    home_page.choose_lang(lang)
    navbar = lang_map["navbar"]
    sidebar = lang_map["sidebar"]

    return [
        (NavbarMsg.POST_ITEM, navbar["posts"], home_page.menu_posts),
        (NavbarMsg.EXPLORE_ITEM, navbar["explore"], home_page.menu_explore),
        (NavbarMsg.SIDEBAR_HOME, sidebar["home"], home_page.sidebar_home),
        (NavbarMsg.SIDEBAR_NEW_POST, sidebar["new_post"], home_page.sidebar_new_post),
        (NavbarMsg.SIDEBAR_DASHBOARD, sidebar["dashboard"], home_page.sidebar_dashboard)
    ]


@log_test_result(test_case_ids=["TC21", "TC22"])
def test_ml_home(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    test_factory.create_post(user)
    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    home_page.choose_lang(lang)
    home = lang_map["home"]

    return [
        (HomeMsg.HOME_TITLE, home["posts"], home_page.page_title),
        (HomeMsg.BTN_NEW_POST, home["new_post"], home_page.new_post)
    ]


@log_test_result(test_case_ids=["TC23", "TC24"])
def test_ml_edit_page(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    post = test_factory.create_post(user)
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Post.NEW_POST)

    editor_page = EditorPage(page)
    editor_page.choose_lang(lang)
    edit = lang_map["edit_page"]

    compare_values = []

    compare_values.extend([
        (EditMsg.BTN_PUBLISH, edit["publish"], editor_page.publish_btn_text),
        (EditMsg.BTN_DRAFT, edit["draft"], editor_page.draft_btn_text),
        (EditMsg.TITLE_PLACEHOLDER, edit["title_placeholder"], editor_page.title_placeholder),
        (EditMsg.SUMMARY_PLACEHOLDER, edit["summary_placeholder"], editor_page.summary_placeholder),
        (EditMsg.CONTENT_PLACEHOLDER, edit["content_placeholder"], editor_page.content_placeholder)
    ])

    page.goto(Auth.HOME)
    home_page = HomePage(page)
    post_item = home_page.post_item_by_article(post.title)
    home_page.edit_btn(post_item).click()

    compare_values.append(
        (EditMsg.BTN_UPDATE, edit["update"], editor_page.update_btn_text)
    )
    return compare_values


@log_test_result(test_case_ids=["TC25", "TC26"])
def test_ml_user_dashboard(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard = lang_map["dashboard_page"]

    compare_value = [
        (DashboardMsg.DASHBOARD_TITLE, dashboard["user_dashboard_title"], dashboard_page.dashboard_title),
        (DashboardMsg.DASHBOARD_DESC, dashboard["user_dashboard_desc"], dashboard_page.dashboard_desc),
        # (DashboardMsg.APPROVE_CARD, dashboard["approved"], dashboard_page.approved_card_text),
        # (DashboardMsg.PENDING_CARD, dashboard["pending"], dashboard_page.pending_card_text),
        # (DashboardMsg.REJECT_CARD, dashboard["rejected"], dashboard_page.rejected_card_text),
        # (DashboardMsg.TOTAL_CARD, dashboard["total"], dashboard_page.total_card_text),
        (DashboardMsg.ACTIVITY_TITLE, dashboard["activity"], dashboard_page.activity_text)
    ]

    expect_card = [dashboard["approved"], dashboard["pending"], dashboard["rejected"], dashboard["total"]]
    actual_card = [dashboard_page.approved_card_text, dashboard_page.pending_card_text, dashboard_page.rejected_card_text, dashboard_page.total_card_text]
    compare_value.append(
        (DashboardMsg.POST_STATISTICS, expect_card, actual_card)
    )

    expected_month = list(lang_map["month"].values())
    actual_month = dashboard_page.month_text_list
    compare_value.append(
        (DashboardMsg.MONTH_COL, expected_month, actual_month)
    )
    # for i in range(len(expected_month)):
    #     compare_value.append(
    #         (DashboardMsg.MONTH_COL.format(num=i+1), expected_month[i], actual_month[i])
    #     )

    return compare_value


@log_test_result(test_case_ids=["TC27", "TC28"])
def test_ml_export_dialog(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard_page.export_btn.click()

    dialog_key = lang_map["export_dialog_key"]
    dialog_map = lang_map["export_dialog"]
    keys = dialog_key.keys()

    actual_select_all_before = dashboard_page.select_all_btn_text
    dashboard_page.select_all_btn.click()
    actual_select_all_after = dashboard_page.select_all_btn_text

    actual_select_post_fields_before = dashboard_page.select_all_post_fields_text
    dashboard_page.select_all_post_fields.click()
    actual_select_post_fields_after = dashboard_page.select_all_post_fields_text

    compare_values = []

    compare_values.extend([
        (DialogMsg.BTN_SELECT_ALL, dialog_map["select_all"], actual_select_all_before),
        (DialogMsg.BTN_DESELECT_ALL, dialog_map["deselect_all"], actual_select_all_after),
        (DialogMsg.BTN_POST_SELECT_ALL, dialog_map["select_all"],  actual_select_post_fields_before),
        (DialogMsg.BTN_POST_DESELECT_ALL, dialog_map["deselect_all"], actual_select_post_fields_after),
        (DialogMsg.BTN_CANCEL, dialog_map["cancel"], dashboard_page.dialog_cancel_btn_text),
        (DialogMsg.BTN_EXPORT, dialog_map["export"], dashboard_page.dialog_export_btn_text)
    ])

    expected_fields = []
    actual_fields = []
    for key in keys:
        expected_fields.append(dialog_key[key])
        actual_fields.append(dashboard_page.label_text((key)))

    compare_values.append(
        ("", expected_fields, actual_fields)
    )
    # for key in keys:
    #     compare_values.append(
    #         (DialogMsg.LABEL.format(name=dialog_key[key].lower()), dialog_key[key], dashboard_page.label_text(key))
    #     )

    return compare_values


@log_test_result(test_case_ids=["TC29", "TC30"])
def test_ml_admin_home(page, test_factory, base_data, lang, lang_map, test_report_file):
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])
    _admin_login(page, payload={"username": admin.username, "password": admin_pw})

    admin_page = AdminPage(page)
    admin_page.choose_lang(lang)

    home = lang_map["admin"]["home"]

    return [
        (AdminHomeMsg.HOME_TITLE, home["admin_dashboard"], admin_page.home_title),
        (AdminHomeMsg.BTN_LOGOUT, home["logout"], admin_page.logout_btn_text),
        (AdminHomeMsg.POST_MANAGE_CARD_TITLE, home["post_manage"], admin_page.post_manage_card_title),
        (AdminHomeMsg.POST_MANAGE_CARD_DESC, home["post_manage_desc"], admin_page.post_manage_card_desc),
        (AdminHomeMsg.BTN_ACCESS, home["access"], admin_page.post_manage_card_btn_text),
        (AdminHomeMsg.BTN_HOME, home["home"], admin_page.home_text),
        (AdminHomeMsg.BTN_POST_MANAGE, home["post_manage"], admin_page.post_management_text)
    ]


@log_test_result(test_case_ids=["TC31", "TC32"])
def test_ml_admin_post_manage(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])
    user, _ = test_factory.create_user(base_data["role_ids"]["user"])
    test_factory.create_post(
        user,
        status="PENDING"
    )
    _admin_login(page, payload={"username": admin.username, "password": admin_pw})

    page.goto(Admin.POST_MANAGE)
    page.wait_for_load_state("networkidle")
    admin_page = AdminPage(page)
    admin_page.choose_lang(lang)
    posts = lang_map["admin"]["posts"]

    compare_values = []

    compare_values.extend([
        (PostManageMsg.POST_STATISTICS_TITLE, posts["statistics"], admin_page.post_stats_card_title),
        (PostManageMsg.POST_STATUS_TITLE, posts["post_ratio"], admin_page.post_ratio_card_title),
        (PostManageMsg.POST_PENDING_LIST, posts["pending_title"], admin_page.post_pending_card_title)
    ])

    expect_header = [posts["title"], posts["author"], posts["created"], posts["status"], posts["action"]]
    actual_header = admin_page.table_header_list

    compare_values.append((PostManageMsg.POST_HEADER, expect_header, actual_header))

    expect_ratio_attributes = [posts["approve"], posts["pending"], posts["reject"]]
    actual_ratio_attributes = admin_page.post_ratio_attribute
    compare_values.append(
        (PostManageMsg.RATIO_ATTRIBUTE, expect_ratio_attributes, actual_ratio_attributes)
    )

    time_range = lang_map["range"]
    options = ["daily", "weekly", "monthly", "yearly"]
    expect_case = [list(time_range[k].values()) for k in options]

    for i in range(len(options)):
        admin_page.dropdown_menu(0).click()
        admin_page.dropdown_option.nth(i).click()
        admin_page.dropdown_menu(1).click()

        case = expect_case[i]
        actual = admin_page.dropdown_option_list

        compare_values.extend([
            (PostManageMsg.OPTION_TYPE.format(name=options[i]), "", ""),
            (PostManageMsg.TIME_CASE, case, actual)
        ])

        admin_page.page.keyboard.press("Escape")
        # admin_page.page.wait_for_selector("[data-state='open']", state="detached")

    admin_page.dropdown_menu(2).click()
    actual_post_status_list = admin_page.dropdown_option_list
    expect_post_status_list = [posts["approve"], posts["reject"]]
    compare_values.append(('', expect_post_status_list, actual_post_status_list))

    return compare_values

