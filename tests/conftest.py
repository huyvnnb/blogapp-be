import base64
import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from playwright.sync_api import Playwright, APIRequestContext
from pytest_html import extras
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from blog import create_app, db
from blog.settings import TestConfig
from blog.users import Role, Users
from blog.utils.helper import get_password_hash
from tests.factories import TestDataFactory
import logging

logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join(os.getcwd(), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

ROOT_DIR = Path(__file__).parent
TEMPLATE_DIR = ROOT_DIR / "test_case"
TEMPLATE_NAME = "KichBanAutomationTest-v3.xlsx"
TEMPLATE_PATH = TEMPLATE_DIR / TEMPLATE_NAME
TEST_CASE_RESULT_DIR = ROOT_DIR / "test_case_result"
TEST_CASE_RESULT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def test_report_file():
    timestamp = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
    test_case_name = TEMPLATE_NAME.split('.')[0]
    report_name = f"{test_case_name}_{timestamp}.xlsx"
    report_file = TEST_CASE_RESULT_DIR / report_name

    try:
        shutil.copyfile(TEMPLATE_PATH, report_file)
        logger.info(f"\nĐã tạo file report: {report_file}")
    except FileNotFoundError:
        pytest.fail(f"LỖI: Không tìm thấy file template gốc tại: {TEMPLATE_PATH}")
    except Exception as e:
        pytest.fail(f"Lỗi khi copy file template: {e}")

    yield report_file
    logger.info(f"\nĐã hoàn tất ghi kết quả vào: {report_file}")


# @pytest.fixture
# def page(playwright):
#     browser = playwright.chromium.launch(headless=True)
#     context = browser.new_context()
#     page = context.new_page()
#     yield page
#     context.close()
#     browser.close()


@pytest.fixture(scope="function")
def test_factory(db_session):
    factory = TestDataFactory(db_session)
    yield factory
    factory.cleanup()


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

# @pytest.fixture(scope="session")
# def app():
#     worker = os.getenv("PYTEST_XDIST_WORKER", "master")
#
#     base_uri = TestConfig.SQLALCHEMY_DATABASE_URI
#     base_name = TestConfig.DB_NAME
#     db_name = f"{base_name}_{worker}"
#
#     admin_uri = (
#         f"postgresql+psycopg://{TestConfig.DB_USER}:{TestConfig.DB_PASSWORD}"
#         f"@{TestConfig.DB_SERVER}:{TestConfig.DB_PORT}/postgres"
#     )
#     admin_engine = create_engine(admin_uri, isolation_level="AUTOCOMMIT")
#
#     with admin_engine.connect() as conn:
#         conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
#         conn.execute(text(f"CREATE DATABASE {db_name}"))
#
#     db_uri = (
#         f"postgresql+psycopg://{TestConfig.DB_USER}:{TestConfig.DB_PASSWORD}"
#         f"@{TestConfig.DB_SERVER}:{TestConfig.DB_PORT}/{db_name}"
#     )
#     TestConfig.SQLALCHEMY_DATABASE_URI = db_uri
#
#     app = create_app(TestConfig)
#     with app.app_context():
#         db.create_all()
#         yield app
#
#         db.session.remove()
#         db.drop_all()
#
#     with admin_engine.connect() as conn:
#         conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))


@pytest.fixture(scope="session")
def base_data(db_session):
    admin_role = Role(name="admin")
    user_role = Role(name="user")
    db_session.add_all([admin_role, user_role])
    db_session.commit()

    admin = Users(
        username="admin",
        display_name="Administrator",
        hashed_password=get_password_hash("password"),
        roles=[admin_role],
    )
    db_session.add(admin)
    db_session.commit()

    return {
        "admin_id": admin.id,
        "role_ids": {"admin": admin_role.id, "user": user_role.id},
    }


@pytest.fixture(scope="session")
def db_session(app):
    with app.app_context():
        connection = db.engine.connect()
        SessionLocal = sessionmaker(bind=connection)
        session = SessionLocal()
        yield session
        session.close()
        connection.close()


@pytest.fixture
def api_request(playwright: Playwright) -> APIRequestContext:
    request_context = playwright.request.new_context(
        base_url="http://localhost:5000"
    )
    yield request_context
    request_context.dispose()


# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_makereport(item: Item, call: CallInfo) -> TestReport:
#     outcome = yield
#     rep: TestReport = outcome.get_result()
#     if rep.when == "call" and rep.failed:
#         page = item.funcargs.get("page")  # type: ignore
#         test_name: str = getattr(item, "name", "unknown_test")
#         if page:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             screenshot_path = os.path.join(REPORTS_DIR, f"{item.name}_{timestamp}.png")
#             try:
#                 page.screenshot(path=screenshot_path, full_page=True)
#                 print(f"Test '{test_name}' failed. Screenshot saved at {screenshot_path}")
#                 print(f"Screenshot path: {screenshot_path}, exists: {os.path.exists(screenshot_path)}")
#
#                 if "html" in item.config.pluginmanager.list_name_plugin():
#                     print("Trying to insert image into report...")
#                     from pytest_html import extras
#                     extra = getattr(rep, "extra", [])
#                     extra.append(extras.image(screenshot_path))
#                     extra.append(extras.text(f"Test '{test_name}' thất bại, xem screenshot."))
#                     rep.extra = extra
#             except Exception as e:
#                 print(f"Cannot take screenshot for {test_name}: {e}")
#     setattr(item, f"rep_{rep.when}", rep)
#     return rep


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page", None)
        if page:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{item.name}_{timestamp}.png"
            screenshot_path = os.path.join(REPORTS_DIR, filename)
            try:
                page.screenshot(path=screenshot_path, full_page=True)
                if os.path.exists(screenshot_path):
                    with open(screenshot_path, "rb") as f:
                        img_bytes = f.read()
                    extra = getattr(rep, "extras", [])
                    encoded = base64.b64encode(img_bytes).decode("utf-8")
                    extra.append(extras.image(encoded, mime_type="image/png", extension="png"))
                    rep.extras = extra
            except Exception as e:
                print(f"Cannot capture screenshot for {item.name}: {e}")
