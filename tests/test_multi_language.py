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


@log_test_result(test_case_ids=["TC12.1", "TC12.2"])
def test_ml_bar(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    home_page.choose_lang(lang)
    navbar = lang_map["navbar"]
    sidebar = lang_map["sidebar"]

    expected = {lang: {"navbar": [], "sidebar": []}}
    actual = {lang: {"navbar": [], "sidebar": []}}

    expected[lang]["navbar"].extend([navbar["posts"], navbar["explore"]])
    expected[lang]["sidebar"].extend([sidebar["home"], sidebar["new_post"], sidebar["dashboard"]])

    actual[lang]["navbar"].extend([home_page.menu_posts, home_page.menu_explore])
    actual[lang]["sidebar"].extend([home_page.sidebar_home, home_page.sidebar_new_post, home_page.sidebar_dashboard])

    return [("", expected, actual)]


@log_test_result(test_case_ids=["TC13.1", "TC13.2"])
def test_ml_home(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    test_factory.create_post(user)
    _login(page, payload={'username': user.username, 'password': password})

    home_page = HomePage(page)
    home_page.choose_lang(lang)
    home = lang_map["home"]

    expected = {lang: {"home": []}}
    actual = {lang: {"home": []}}
    expected[lang]["home"].extend([home["posts"], home["new_post"]])
    actual[lang]["home"].extend([home_page.page_title, home_page.new_post])

    return [
        ("", expected, actual)
    ]


@log_test_result(test_case_ids=["TC14.1", "TC14.2"])
def test_ml_edit_page(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    test_factory.create_post(user)
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Post.NEW_POST)

    editor_page = EditorPage(page)
    editor_page.choose_lang(lang)
    edit = lang_map["edit_page"]

    expected = {
        lang: {
            "edit": [
                edit["publish"],
                edit["draft"],
                edit["title_placeholder"],
                edit["summary_placeholder"],
                edit["content_placeholder"]
            ]
        }
    }
    actual = {
        lang: {
            "edit": [
                editor_page.publish_btn_text,
                editor_page.draft_btn_text,
                editor_page.title_placeholder,
                editor_page.summary_placeholder,
                editor_page.content_placeholder
            ]
        }
    }

    return [
        (EditMsg.EDIT_PAGE, expected, actual)
    ]


@log_test_result(test_case_ids=["TC15.1", "TC15.2"])
def test_ml_user_dashboard_heading(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard = lang_map["dashboard_page"]

    expected = {lang: {"header": dashboard["user_dashboard_title"], "desc": dashboard["user_dashboard_desc"]}}
    actual = {lang: {"header": dashboard_page.dashboard_title, "desc": dashboard_page.dashboard_desc}}

    return [
        (DashboardMsg.DASHBOARD_TITLE, expected, actual)
    ]


@log_test_result(test_case_ids=["TC16.1", "TC16.2"])
def test_ml_user_dashboard_post_status_card(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard = lang_map["dashboard_page"]

    expected = {
        lang: {
            "cards": [
                dashboard["approved"],
                dashboard["pending"],
                dashboard["rejected"],
                dashboard["total"]
            ]
        }
    }

    actual = {
        lang: {
            "cards": [
                dashboard_page.approved_card_text,
                dashboard_page.pending_card_text,
                dashboard_page.rejected_card_text,
                dashboard_page.total_card_text
            ]
        }
    }

    return [
        (DashboardMsg.POST_STATISTICS, expected, actual)
    ]


@log_test_result(test_case_ids=["TC17.1", "TC17.2"])
def test_ml_user_dashboard_activity(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard = lang_map["dashboard_page"]

    expected = {
        lang: {
            "header": dashboard["activity"],
            "months": list(lang_map["month"].values())
        }
    }
    actual = {
        lang: {
            "header": dashboard_page.activity_text,
            "months": dashboard_page.month_text_list
        }
    }

    return [
        (DashboardMsg.ACTIVITY_TITLE, expected, actual)
    ]


@log_test_result(test_case_ids=["TC18.1", "TC18.2"])
def test_ml_export_dialog_check_button(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard_page.export_btn.click()

    dialog_map = lang_map["export_dialog"]

    actual_select_all_before = dashboard_page.select_all_btn_text
    dashboard_page.select_all_btn.click()
    actual_select_all_after = dashboard_page.select_all_btn_text

    actual_select_post_fields_before = dashboard_page.select_all_post_fields_text
    dashboard_page.select_all_post_fields.click()
    actual_select_post_fields_after = dashboard_page.select_all_post_fields_text

    expected = {
        lang: {
            "buttons": [
                dialog_map["select_all"],
                dialog_map["deselect_all"],
                dialog_map["select_all"],
                dialog_map["deselect_all"],
                dialog_map["cancel"],
                dialog_map["export"],
            ]
        }
    }
    actual = {
        lang: {
            "buttons": [
                actual_select_all_before,
                actual_select_all_after,
                actual_select_post_fields_before,
                actual_select_post_fields_after,
                dashboard_page.dialog_cancel_btn_text,
                dashboard_page.dialog_export_btn_text
            ]
        }
    }

    return [
        ("", expected, actual)
    ]


@log_test_result(test_case_ids=["TC19.1", "TC19.2"])
def test_ml_export_dialog_summary_fields(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard_page.export_btn.click()

    dialog_key = lang_map["export_dialog_key"]
    keys = [
        "user_info",
        "avg_length",
        "export_posts",
        "total_posts",
        "approval_rate"
    ]

    expected_fields = []
    actual_fields = []
    for key in keys:
        expected_fields.append(dialog_key[key])
        actual_fields.append(dashboard_page.label_text(key))

    expected = {
        lang: {
            "summary_options": expected_fields
        }
    }
    actual = {
        lang: {
            "summary_options": actual_fields
        }
    }

    return [
        ("", expected, actual)
    ]


@log_test_result(test_case_ids=["TC20.1", "TC20.2"])
def test_ml_export_dialog_post_fields(page, test_factory, base_data, lang, lang_map, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])
    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)
    dashboard_page.choose_lang(lang)
    dashboard_page.export_btn.click()

    dialog_key = lang_map["export_dialog_key"]
    keys = [
        "post_id",
        "post_title",
        "post_content",
        "post_summary",
        "post_user_id",
        "post_published",
        "post_is_public",
        "post_status",
        "post_created_at",
        "post_updated_at"
    ]

    dashboard_page.select_all_btn.click()

    expected_fields = []
    actual_fields = []
    for key in keys:
        expected_fields.append(dialog_key[key])
        actual_fields.append(dashboard_page.label_text(key))

    expected = {
        lang: {
            "post_options": expected_fields
        }
    }
    actual = {
        lang: {
            "post_options": actual_fields
        }
    }

    return [
        ("", expected, actual)
    ]


@log_test_result(test_case_ids=["TC21.1", "TC21.2"])
def test_ml_admin_home_navigation(page, test_factory, base_data, lang, lang_map, test_report_file):
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])
    _admin_login(page, payload={"username": admin.username, "password": admin_pw})

    admin_page = AdminPage(page)
    admin_page.choose_lang(lang)

    home = lang_map["admin"]["home"]

    expected = {lang: {"sidebar": [home["logout"], home["home"], home["post_manage"]]}}
    actual = {lang: {"sidebar": [admin_page.logout_btn_text, admin_page.home_text, admin_page.post_management_text]}}

    return [
        (AdminHomeMsg.ADMIN_HOME, expected, actual)
    ]


@log_test_result(test_case_ids=["TC22.1", "TC22.2"])
def test_ml_admin_home_menu(page, test_factory, base_data, lang, lang_map, test_report_file):
    admin, admin_pw = test_factory.create_user(base_data["role_ids"]["admin"])
    _admin_login(page, payload={"username": admin.username, "password": admin_pw})

    admin_page = AdminPage(page)
    admin_page.choose_lang(lang)

    home = lang_map["admin"]["home"]

    expected = {
        lang: {
            "header": home["admin_dashboard"],
            "cards": [
                home["post_manage"],
                home["post_manage_desc"],
                home["access"]
            ]
        }
    }

    actual = {
        lang: {
            "header": admin_page.home_title,
            "cards": [
                admin_page.post_manage_card_title,
                admin_page.post_manage_card_desc,
                admin_page.post_manage_card_btn_text
            ]
        }
    }

    return [
        (AdminHomeMsg.ADMIN_HOME, expected, actual)
    ]


@log_test_result(test_case_ids=["TC23.1", "TC23.2"])
def test_ml_admin_post_manage_post_stats(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
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

    time_range = lang_map["range"]
    options = ["daily", "weekly", "monthly", "yearly"]

    time_case = {k: list(time_range[k].values()) for k in options}

    expected = {
        lang: {
            "header": posts["statistics"],
            "time_case": time_case,
            "status_options": [posts["approve"], posts["reject"]]
        }
    }

    actual_time_case = {}
    for i, k in enumerate(options):
        admin_page.dropdown_menu(0).click()
        admin_page.dropdown_option.nth(i).click()
        admin_page.dropdown_menu(1).click()
        actual_time_case[k] = admin_page.dropdown_option_list
        admin_page.page.keyboard.press("Escape")

    admin_page.dropdown_menu(2).click()
    actual_post_status_list = admin_page.dropdown_option_list
    admin_page.page.keyboard.press("Escape")

    actual = {
        lang: {
            "header": admin_page.post_stats_card_title,
            "time_case": actual_time_case,
            "status_options": actual_post_status_list
        }
    }

    return [
        ("", expected, actual)
    ]


@log_test_result(test_case_ids=["TC24.1", "TC24.2"])
def test_ml_admin_post_manage_status_ratio(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
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

    expected = {
        lang: {
            "header": posts["post_ratio"],
            "attributes": [posts["approve"], posts["pending"], posts["reject"]]
        }
    }
    actual = {
        lang: {
            "header": admin_page.post_ratio_card_title,
            "attributes": admin_page.post_ratio_attribute
        }
    }

    return [("", expected, actual)]


@log_test_result(test_case_ids=["TC25.1", "TC25.2"])
def test_ml_admin_post_manage_pending_post(page: Page, test_factory, base_data, lang, lang_map, test_report_file):
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

    expected = {
        lang: {
            "header": posts["pending_title"],
            "columns": [
                posts["title"],
                posts["author"],
                posts["created"],
                posts["status"],
                posts["action"]
            ]
        }
    }

    actual = {
        lang: {
            "header": admin_page.post_pending_card_title,
            "columns": admin_page.table_header_list
        }
    }

    return [("", expected, actual)]

