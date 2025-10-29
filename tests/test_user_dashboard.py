from pathlib import Path

import openpyxl
from playwright.sync_api import Page, expect

from tests.endpoints import Dashboard
from tests.pages import DashboardPage
from tests.test_user_auth import _login


def test_post_status(page: Page, test_factory, base_data):
    # page.set_viewport_size({"width": 1920, "height": 1080})
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    approve_count = 20
    pending_count = 15
    reject_count = 10
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
        title_pref="Approve post",
        summary="Approve summary",
        content="Approve content",
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

    _login(page, payload={'username': user.username, 'password': password})

    page.goto(Dashboard.DASHBOARD)
    dashboard_page = DashboardPage(page)

    dashboard_page.post_status_card.is_visible(timeout=5000)
    expect(dashboard_page.approve_count).to_have_text(str(approve_count))
    expect(dashboard_page.pending_count).to_have_text(str(pending_count))
    expect(dashboard_page.reject_count).to_have_text(str(reject_count))
    expect(dashboard_page.total_count).to_have_text(str(total_count))


def test_export_data(page: Page, test_factory, base_data):
    user, password = test_factory.create_user(base_data["role_ids"]["user"])

    approve_count = 20
    pending_count = 15
    reject_count = 10
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
    print(f"Total posts: {len(all_posts)}")
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
        "post_summary",
        "post_created_at"
    ]
    dashboard_page.select_checkbox(ids)
    with page.expect_download() as download_info:
        confirm_export.click()

    download = download_info.value

    print("File name:", download.suggested_filename)

    download_dir = Path("./downloads")
    download_dir.mkdir(exist_ok=True)

    path = download.path()
    print(f"Path: {path}")
    file_path = download_dir / download.suggested_filename
    download.save_as(str(file_path))
    print(f"File saved at: {file_path}")

    import os
    assert os.path.exists(f"./downloads/{download.suggested_filename}")
    assert os.path.getsize(f"./downloads/{download.suggested_filename}") > 0

    expected_headers = ["User ID", "Username", "Display name", "Total post", "Average words", "Approval rate"]
    expected_post_headers = ["id", "title", "summary", "created_at"]

    wb = openpyxl.load_workbook(file_path)
    print("Tên các sheet:", wb.sheetnames)
    sheet_names = wb.sheetnames

    summary_sheet = wb[sheet_names[0]]
    posts_sheet = wb[sheet_names[1]]

    actual_headers = [cell.value for cell in summary_sheet[1]]
    actual_post_headers = [cell.value for cell in posts_sheet[1]]

    assert actual_headers == expected_headers
    assert actual_post_headers == expected_post_headers

    summary_row = list(summary_sheet.iter_rows(min_row=2, values_only=True))[0]

    uid, username, display_name, total_post, avg_words, approval_rate = summary_row
    total_words = sum(len(post.content.split()) for post in all_posts)
    expected_avg = total_words // len(all_posts) if all_posts else 0
    expected_approval = approve_count * 100 / total_count if total_count else 0

    assert uid == user.id
    assert username == user.username
    assert display_name == user.display_name
    assert total_post == total_count
    assert int(avg_words) == expected_avg
    assert approval_rate == f"{expected_approval:.2f}%"

    actual_posts = {(row[0], row[1], row[2], row[3].replace(microsecond=0)) for row in posts_sheet.iter_rows(min_row=2, values_only=True)}
    expect_post = {(post.id, post.title, post.summary, post.created_at.replace(microsecond=0)) for post in all_posts}

    assert actual_posts == expect_post

    if file_path.exists():
        os.remove(file_path)

