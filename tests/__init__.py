import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# @pytest.fixture
# def driver():
#     chrome_options = Options()
#
#     prefs = {
#         "credentials_enable_service": False,  # tắt dịch vụ lưu mật khẩu
#         "profile.password_manager_enabled": False  # tắt gợi ý lưu mật khẩu
#     }
#     chrome_options.add_experimental_option("prefs", prefs)
#     chrome_options.add_argument("--disable-blink-features=CredentialManagement")
#     chrome_options.add_argument("--disable-notifications")
#
#     driver = webdriver.Chrome()
#     driver.maximize_window()
#     yield driver
#     driver.quit()