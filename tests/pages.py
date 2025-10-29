from typing import List, Union, Optional

from playwright.sync_api import Page, Locator, Response
import unicodedata


def norm(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip())


class NavBar:
    def __init__(self, page: Page):
        self.page = page

    @property
    def header(self) -> Locator:
        return self.page.locator("header")

    @property
    def search_bar(self) -> Locator:
        return self.header.locator("button[data-slot='button']")

    @property
    def search_result(self) -> Locator:
        return self.page.locator("div.overflow-hidden")

    @property
    def search_field(self) -> Locator:
        return self.search_result.locator("input[data-slot='input']")

    @property
    def result_field(self) -> Locator:
        return self.search_result.locator("div.p-4.overflow-y-auto")

    @property
    def all_posts(self) -> Locator:
        return self.page.locator("div.block.p-3")

    def post_search_with_title(self, title: str) -> Locator:
        return self.page.locator("div.block.p-3", has_text=title)

    def post_search_title(self, post_item: Locator) -> str:
        title_el = post_item.locator("p.font-medium")
        title_el.scroll_into_view_if_needed()
        title_el.wait_for(state="attached", timeout=3000)
        return title_el.inner_text().strip()

    def post_search_author(self, post_item: Locator) -> str:
        author = post_item.locator("a").nth(0)
        author.scroll_into_view_if_needed()
        author.wait_for(state="attached", timeout=5000)
        return author.inner_text().strip()

    @property
    def menu_option(self) -> Locator:
        return self.header.locator("button[data-slot='dropdown-menu-trigger']").nth(1)

    def logout(self):
        self.page.locator("div[role='menuitem']", has_text="Logout").click()

    # Multi-language component
    @property
    def menu_posts(self) -> str:
        return self.header.locator("a[href='/home']").inner_text().strip()

    @property
    def menu_explore(self) -> str:
        return self.header.locator("a[href='/explore']").inner_text().strip()

    @property
    def multi_lang(self) -> Locator:
        return self.header.locator("button[data-slot='dropdown-menu-trigger']").nth(0)

    def choose_lang(self, lang: str = "vi"):
        self.multi_lang.click()
        if lang == "vi":
            self.page.locator("div[role='menuitem']").nth(0).click()
        else:
            self.page.locator("div[role='menuitem']").nth(1).click()


class HomePage(NavBar):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.article_area = self.page.locator("[class*='grid'][class*='gap-6']")

    def post_item_by_article(self, title: str) -> Locator:
        return self.page.locator(f"[data-slot='card']:has-text('{title}')")

    def post_title(self, post_item: Locator):
        title_el = post_item.locator("[data-slot='card-title']").nth(0)
        title_el.wait_for()
        return title_el.inner_text().strip()

    def badge(self, post_item: Locator, pos: int) -> str:
        badge_el = post_item.locator("[data-slot='badge']").nth(pos)
        badge_el.wait_for(timeout=5000)
        return badge_el.inner_text().strip()

    def edit_btn(self, post_item: Locator) -> Locator:
        return post_item.locator("button").nth(0)

    def delete_btn(self, post_item: Locator) -> Locator:
        return post_item.locator("button").nth(1)

    def all_post_items(self):
        return self.page.locator("[data-slot='card']")

    # Multi-language component
    @property
    def sidebar(self):
        return self.page.locator("aside.fixed")

    @property
    def sidebar_home(self) -> str:
        return self.sidebar.locator("a[href='/home']").inner_text()

    @property
    def sidebar_new_post(self) -> str:
        return self.sidebar.locator("a[href='/posts/new']").inner_text()

    @property
    def sidebar_dashboard(self) -> str:
        return self.sidebar.locator("a[href='/dashboard']").inner_text()

    @property
    def new_post(self) -> str:
        return self.page.locator('button[data-slot="button"].bg-primary').inner_text()

    @property
    def page_title(self) -> str:
        return self.page.locator("h1.text-text").inner_text()


class EditorPage(NavBar):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.tab_content = self.page.locator("div[role='tabpanel'][data-slot='tabs-content']")
        self.parent_btn_div = self.page.locator("div.flex.justify-end.gap-2.mt-4")

    @property
    def title_input(self) -> Locator:
        return self.tab_content.locator("input").nth(0)

    @property
    def summary_input(self) -> Locator:
        return self.tab_content.locator("textarea").nth(0)

    @property
    def content_input(self) -> Locator:
        return self.tab_content.locator("textarea").nth(1)

    def fill_title(self, title: str):
        self.title_input.fill(title)

    def fill_summary(self, summary: str):
        self.summary_input.fill(summary)

    def fill_content(self, content: str):
        self.content_input.fill(content)

    def select_dropdown_option(self, dropdown_index: int, option_text: str):
        dropdown = self.page.locator("button[role='combobox'][data-slot='select-trigger']").nth(dropdown_index)
        dropdown.click()
        option = self.page.locator(f"div[role='option']:has-text('{option_text}')")
        option.wait_for(state="visible")
        option.click()

    def _click_button(self, pos: int):
        btn = self.parent_btn_div.locator("button").nth(pos)
        return btn

    def save_draft(self):
        with self.page.expect_response(lambda r: "/posts" in r.url):
            self._click_button(0).click()

    def publish(self) -> Response:
        with self.page.expect_response(lambda r: "/posts" in r.url) as resp_info:
            self._click_button(1).click()

        return resp_info.value

    def update(self):
        with self.page.expect_response(lambda r: "/posts" in r.url) as resp_info:
            self._click_button(0).click()

        return resp_info.value

    # Multi-language components
    @property
    def update_btn_text(self):
        return self._click_button(0).inner_text()

    @property
    def publish_btn_text(self):
        return self._click_button(1).inner_text()

    @property
    def draft_btn_text(self):
        return self._click_button(0).inner_text()

    @property
    def title_placeholder(self):
        return self.title_input.get_attribute("placeholder")

    @property
    def summary_placeholder(self):
        return self.summary_input.get_attribute("placeholder")

    @property
    def content_placeholder(self):
        return self.content_input.get_attribute("placeholder")


class DashboardPage(NavBar):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    @property
    def post_status_card(self):
        return self.page.locator("section").nth(0)

    def post_status_count(self, pos: int):
        return self.post_status_card.locator("div.text-2xl").nth(pos)

    @property
    def approve_count(self) -> Locator:
        return self.post_status_count(0)

    @property
    def pending_count(self) -> Locator:
        return self.post_status_count(1)

    @property
    def reject_count(self) -> Locator:
        return self.post_status_count(2)

    @property
    def total_count(self) -> Locator:
        return self.post_status_count(3)

    @property
    def export_btn(self):
        return self.page.locator("#export-excel-btn")

    @property
    def export_dialog_option(self):
        return self.page.locator("div.flex-col-reverse.justify-end")

    def confirm_export(self):
        return self.export_dialog_option.locator("button").nth(1)

    def cancel_export(self):
        return self.export_dialog_option.locator("button").nth(0)

    def toggle_checkbox(self, checkbox_id: str, check: bool = True):
        checkbox = self.page.locator(f"button[role='checkbox']#{checkbox_id}")

        current = checkbox.get_attribute("aria-checked") == "true"

        if current != check:
            checkbox.click()

    def select_checkbox(self, ids: Union[str, List[str]]):
        if isinstance(ids, str):
            ids = [ids]

        for id in ids:
            self.toggle_checkbox(id)

    def dialog_btn(self, pos: int) -> Locator:
        return self.export_dialog.locator("button[data-slot='button']").nth(pos)

    @property
    def select_all_btn(self) -> Locator:
        return self.dialog_btn(0)

    @property
    def select_all_post_fields(self) -> Locator:
        return self.dialog_btn(1)

    @property
    def dialog_cancel_btn(self) -> Locator:
        return self.dialog_btn(2)

    @property
    def dialog_export_btn(self) -> Locator:
        return self.dialog_btn(3)

    # Multi-language component
    @property
    def dashboard_title(self) -> str:
        return self.page.locator("h1.text-4xl").inner_text()

    @property
    def dashboard_desc(self) -> str:
        return self.page.locator("p.truncate").inner_text()

    def post_status_card_header(self, pos: int) -> str:
        return self.post_status_card.locator("div[data-slot='card-title']").nth(pos).inner_text()

    @property
    def approved_card_text(self) -> str:
        return self.post_status_card_header(0)

    @property
    def pending_card_text(self) -> str:
        return self.post_status_card_header(1)

    @property
    def rejected_card_text(self) -> str:
        return self.post_status_card_header(2)

    @property
    def total_card_text(self) -> str:
        return self.post_status_card_header(3)

    @property
    def activity_section(self) -> Locator:
        return self.page.locator("section").nth(1)

    @property
    def activity_text(self) -> str:
        return self.activity_section.locator("div[data-slot='card-title']").inner_text().split("(")[0]

    @property
    def month_text_list(self) -> list[str]:
        months = self.activity_section.locator("span.text-xs")
        month_str = []
        for i in range(months.count()):
            month_str.append(months.nth(i).inner_text())

        return month_str

    @property
    def export_dialog(self) -> Locator:
        return self.page.locator("div[role='dialog']")

    @property
    def dialog_title(self) -> str:
        return self.export_dialog.locator("h2").inner_text()

    def dialog_desc(self) -> str:
        return self.export_dialog.locator("p.text-sm").inner_text()

    def label_text(self, key: str) -> str:
        return self.page.locator(f"label[for='{key}']").inner_text()

    @property
    def select_all_btn_text(self):
        return self.select_all_btn.inner_text()

    @property
    def select_all_post_fields_text(self):
        return self.select_all_post_fields.inner_text()

    @property
    def dialog_cancel_btn_text(self) -> str:
        return self.dialog_cancel_btn.inner_text()

    @property
    def dialog_export_btn_text(self) -> str:
        return self.dialog_export_btn.inner_text()


class AdminSidebar:
    def __init__(self, page: Page):
        self.page = page

    @property
    def sidebar(self):
        return self.page.locator("div.fixed.left-0.top-0")

    @property
    def home(self):
        return self.page.locator("a[href='/admin']")

    @property
    def post_management(self):
        return self.page.locator("a[href='/admin/posts']")

    # Multi-language component
    @property
    def home_text(self):
        return self.home.inner_text()

    @property
    def post_management_text(self):
        return self.post_management.inner_text()

    @property
    def multi_lang(self):
        return self.page.locator("button[data-slot='dropdown-menu-trigger']")

    def choose_lang(self, lang: str = "vi"):
        self.multi_lang.click()
        if lang == "vi":
            self.page.locator("div[role='menuitem']").nth(0).click()
        else:
            self.page.locator("div[role='menuitem']").nth(1).click()

    # @property
    # def logout_btn(self):
    #     return self.sidebar.locator("button[data-slot='button']")
    #
    # def logout(self):
    #     return self.logout_btn.click()


class AdminPage(AdminSidebar):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    @property
    def pending_list(self):
        # return self.page.locator("tr[data-slot='table-row']")
        return self.page.locator('tbody[data-slot="table-body"] tr[data-slot="table-row"]')

    def pending_item(self, title: str) -> Locator:
        return self.pending_list.filter(has=self.page.locator(f"td.font-medium:has-text('{title}')"))

    def pending_title(self, pending_item: Locator) -> str:
        return pending_item.locator("td[data-slot='table-cell']").nth(0).inner_text()

    def approve_btn(self, pending_item: Locator) -> Locator:
        return pending_item.locator("button").nth(0)

    def reject_btn(self, pending_item: Locator) -> Locator:
        return pending_item.locator("button").nth(1)

    def approve(self, pending_item: Locator):
        self.approve_btn(pending_item).click()

    def reject(self, pending_item: Locator):
        self.reject_btn(pending_item).click()

    def dropdown_menu(self, pos: Optional[int]):
        selector = self.page.locator("button[role='combobox']")
        if pos is not None:
            selector = selector.nth(pos)
        return selector

    @property
    def dropdown_option(self):
        return self.page.locator("div[role='option'] span:nth-of-type(2)")

    @property
    def dropdown_type(self):
        return self.dropdown_menu(pos=0)

    @property
    def dropdown_range(self):
        return self.dropdown_menu(pos=1)

    @property
    def dropdown_status(self):
        return self.dropdown_menu(pos=2)

    @property
    def logout_btn(self):
        return self.page.locator('button:has(svg.lucide-log-out)')

    def logout(self):
        self.logout_btn.click()

    # Multi-language component
    @property
    def logout_btn_text(self) -> str:
        return self.logout_btn.inner_text()

    @property
    def home_title(self) -> str:
        return self.page.locator("h1.text-3xl").inner_text()

    @property
    def post_manage_card(self) -> Locator:
        return self.page.locator("div[data-slot='card']").nth(0)

    @property
    def post_manage_card_title(self) -> str:
        return self.post_manage_card.locator("div[data-slot='card-title']").inner_text()

    @property
    def post_manage_card_desc(self) -> str:
        return self.post_manage_card.locator("p").inner_text()

    @property
    def post_manage_card_btn_text(self) -> str:
        return self.post_manage_card.locator("button").inner_text()

    def card_title(self, pos: int) -> str:
        return self.page.locator("div[data-slot='card-title']").nth(pos).inner_text()

    @property
    def post_stats_card_title(self) -> str:
        return self.card_title(0)

    @property
    def post_ratio_card_title(self) -> str:
        return self.card_title(1)

    @property
    def post_pending_card_title(self) -> str:
        return self.card_title(2)

    @property
    def table_header(self):
        return self.page.locator("th[data-slot='table-head']")

    @property
    def table_header_list(self) -> list[str]:
        header = []
        for i in range(self.table_header.count()):
            header.append(self.table_header.nth(i).inner_text())

        return header

    @property
    def post_ratio_attribute(self) -> list[str]:
        selector = self.page.locator("span.recharts-legend-item-text")
        attributes = []
        for i in range(selector.count()):
            attributes.append(selector.nth(i).inner_text())

        return attributes

    @property
    def dropdown_option_list(self) -> list[str]:
        options = []
        for i in range(self.dropdown_option.count()):
            options.append(self.dropdown_option.nth(i).inner_text())

        return options




