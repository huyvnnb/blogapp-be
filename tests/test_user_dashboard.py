from pathlib import Path

import openpyxl
from playwright.sync_api import Page, expect

from tests.endpoints import Dashboard
from tests.messages import DashboardMsg, DialogMsg
from tests.pages import DashboardPage
from tests.test_user_auth import _login
from tests.testcase_helper import log_test_result
import pytest_check as check


@log_test_result(test_case_ids="TC11")
def test_post_status(page: Page, test_factory, base_data, test_report_file):
    # page.set_viewport_size({"width": 1920, "height": 1080})
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    approve_count = 3
    pending_count = 2
    reject_count = 1
    total_count = approve_count + pending_count + reject_count

    test_factory.create_posts(
        user,
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
        status="APPROVE",
        count=approve_count
    )

    test_factory.create_posts(
        user,
        title_pref="Pending post",
        summary="Pending summary",
        content="Pending content",
        status="PENDING",
        count=pending_count
    )

    test_factory.create_posts(
        user,
        title_pref="Reject post",
        summary="Reject summary",
        content="Reject content",
        status="REJECT",
        count=reject_count
    )

    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)

    dashboard_page.post_status_card.is_visible(timeout=5000)
    actual_approve = dashboard_page.approve_count.inner_text()
    actual_pending = dashboard_page.pending_count.inner_text()
    actual_reject = dashboard_page.reject_count.inner_text()
    actual_total = dashboard_page.total_count.inner_text()

    # compare_values = [
    #     (DashboardMsg.APPROVE_COUNT, approve_count, dashboard_page.approve_count.inner_text()),
    #     (DashboardMsg.PENDING_COUNT, pending_count, dashboard_page.pending_count.inner_text()),
    #     (DashboardMsg.REJECT_COUNT, reject_count, dashboard_page.reject_count.inner_text()),
    #     (DashboardMsg.TOTAL_COUNT, total_count, dashboard_page.total_count.inner_text())
    # ]

    return [
        (
            DashboardMsg.POST_STATISTICS,
            [str(approve_count), str(pending_count), str(reject_count), str(total_count)],
            [actual_approve, actual_pending, actual_reject, actual_total]
        )
    ]


@log_test_result(test_case_ids="TC12")
def test_export_data(page: Page, test_factory, base_data, test_report_file):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    approve_count = 1
    pending_count = 1
    reject_count = 1
    total_count = approve_count + pending_count + reject_count

    all_posts = test_factory.create_posts(
        user,
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
        status="APPROVE",
        count=approve_count
    )

    all_posts.extend(test_factory.create_posts(
        user,
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
        status="PENDING",
        count=pending_count
    ))

    all_posts.extend(test_factory.create_posts(
        user,
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
        status="REJECT",
        count=reject_count
    ))
    _login(page, payload={'username': user.username, 'password': password})
    page.goto(Dashboard.DASHBOARD)

    dashboard_page = DashboardPage(page)

    export_btn = dashboard_page.export_btn
    export_btn.click()

    confirm_export = dashboard_page.confirm_export()
    ids = [
        "user_info",
        "total_posts",
        "avg_length",
        "approval_rate",
        "export_posts",
        "post_id",
        "post_title",
        "post_content",
        "post_summary",
        "post_user_id",
        "post_published",
        "post_is_public",
        "post_status",
        "post_created_at",
        "post_updated_at",
    ]
    dashboard_page.select_checkbox(ids)
    with page.expect_download() as download_info:
        confirm_export.click()

    download = download_info.value

    download_dir = Path("./downloads")
    download_dir.mkdir(exist_ok=True)

    path = download.path()
    print(f"Path: {path}")
    file_path = download_dir / download.suggested_filename
    download.save_as(str(file_path))
    print(f"File saved at: {file_path}")

    import os
    compare_values = []
    if os.path.exists(file_path):
        compare_values = [(DialogMsg.FILE_FOUND.format(file_name=download.suggested_filename), "", "")]
    else:
        compare_values.append((DialogMsg.FILE_NOT_FOUND.format(file_name=download.suggested_filename), "", ""))
        check.fail("File download thất bại hoặc file trống.")
        return compare_values

    expected_headers = ["User ID", "Username", "Display name", "Total post", "Average words", "Approval rate"]

    wb = openpyxl.load_workbook(file_path)
    print("Tên các sheet:", wb.sheetnames)
    sheet_names = wb.sheetnames

    summary_sheet = wb[sheet_names[0]]
    posts_sheet = wb[sheet_names[1]]

    summary_data = list(summary_sheet.iter_rows(min_row=1, values_only=True))
    header_row = list(summary_data[0])
    summary_row = list(summary_data[1])

    uid, username, display_name, total_post, avg_words, approval_rate = summary_row
    total_words = sum(len(post.content.split()) for post in all_posts)
    expected_avg = total_words // len(all_posts) if all_posts else 0
    expected_approval = approve_count * 100 / total_count if total_count else 0

    expected_summary = [user.id, user.username, user.display_name, total_count, expected_avg, f"{expected_approval:.2f}%"]
    actual_summary = [uid, username, display_name, total_post, int(avg_words), approval_rate]

    compare_values.extend([
        (DialogMsg.FIELD_SUMMARY_HEADER, expected_headers, header_row),
        (DialogMsg.FIELD_SUMMARY_DATA, expected_summary, actual_summary)
    ])

    posts_data = list(posts_sheet.iter_rows(min_row=1, values_only=True))
    expected_post_headers = ["id", "title", "content", "summary", "user_id", "published", "is_public", "status", "created_at", "updated_at"]
    actual_post_headers = list(posts_data[0])

    compare_values.append(
        (DialogMsg.POST_DETAIL_HEADER, expected_post_headers, actual_post_headers)
    )

    actual_posts = {
        (
            int(row[0]), str(row[1]), str(row[2]), str(row[3]), int(row[4]),
            bool(row[5]), bool(row[6]), str(row[7]),
            row[8].replace(microsecond=0), row[9].replace(microsecond=0)
        )
        for row in posts_data[1:]
    }

    expect_posts = {
        (
            int(post.id), str(post.title), str(post.content), str(post.summary), int(post.user_id),
            bool(post.published), bool(post.is_public), str(post.status),
            post.created_at.replace(microsecond=0), post.updated_at.replace(microsecond=0)
        )
        for post in all_posts
    }

    matches = expect_posts & actual_posts
    missing = expect_posts - actual_posts
    extra = actual_posts - expect_posts

    for item in matches:
        compare_values.append((DialogMsg.POST_DETAIL_DATA, item, item))

    for item in missing:
        compare_values.append((DialogMsg.POST_DETAIL_DATA, item, "-"))

    for item in extra:
        compare_values.append((DialogMsg.POST_DETAIL_DATA, "-", item))

    if file_path.exists():
        os.remove(file_path)

    return compare_values

