class Message:
    STATUS = "Mã trạng thái"
    URL_PATH = "Đường dẫn trang hiện tại"
    SEP = "------------{content}------------"

    POST_INFO = "Thông tin bài viết"
    POST_TITLE = "Tiêu đề bài viết"
    POST_AUTHOR = "Tác giả"

    BADGE_APPROVE = "Trạng thái chấp nhận"
    BADGE_PUBLIC = "Trạng thái công khai"
    BADGE_PUBLISH = "Trạng thái xuất bản"

    PRE_BADGE_APPROVE = "Trạng thái chấp nhận trước"
    PRE_BADGE_PUBLIC = "Trạng thái công khai trước"
    PRE_BADGE_PUBLISH = "Trạng thái xuất bản trước"

    POST_BADGE_APPROVE = "Trạng thái chấp nhận sau"
    POST_BADGE_PUBLIC = "Trạng thái công khai sau"
    POST_BADGE_PUBLISH = "Trạng thái xuất bản sau"

    POST_VISIBILITY = "Trạng thái hiển thị"
    VISIBLE = "Hiển thị"
    INVISIBLE = "Không hiển thị"

    POST_COUNT = "Tổng số lượng bài viết"
    POST_SEARCH_COUNT = "Tổng số bài tìm kiếm"

    ERROR = "Đã có lỗi xảy ra: {error}"


class NavbarMsg:
    POST_ITEM = "Nút danh sách bài viết"
    EXPLORE_ITEM = "Nút khám phá"
    SIDEBAR_HOME = "Nút trang chủ"
    SIDEBAR_NEW_POST = "Nút tạo bài viết mới"
    SIDEBAR_DASHBOARD = "Nút trang điều khiển"


class HomeMsg:
    HOME_TITLE = "Tiêu đề trang"
    BTN_NEW_POST = "Nút tạo bài viết mới"


class EditMsg:
    EDIT_PAGE = "Trang chỉnh sửa bài viết"
    BTN_PUBLISH = "Nút xuất bản bài viết"
    BTN_DRAFT = "Nút lưu bản nháp"
    BTN_UPDATE = "Nút cập nhật bài viết"

    TITLE_PLACEHOLDER = "Tiêu đề gợi ý"
    SUMMARY_PLACEHOLDER = "Tóm tắt gợi ý"
    CONTENT_PLACEHOLDER = "Nội dung gợi ý"
    # OPTION_PUBLIC = "Lựa chọn công khai"
    # OPTION_PRIVATE = "Lựa chọn riêng tư"


class DashboardMsg:
    DASHBOARD_TITLE = "Tiêu đề trang điều khiển"
    DASHBOARD_DESC = "Mô tả trang điều khiển"

    POST_STATISTICS = "Thống kê bài viết"
    APPROVE_CARD = "Thẻ bài viết được chấp nhận"
    PENDING_CARD = "Thẻ bài viết đang chờ"
    REJECT_CARD = "Thẻ bài viết bị từ chối"
    TOTAL_CARD = "Thẻ tổng số bài viết"

    APPROVE_COUNT = "Số lượng bài viết được chấp nhận"
    PENDING_COUNT = "Số lượng bài viết đang chờ"
    REJECT_COUNT = "Số lượng bài viết bị từ chối"
    TOTAL_COUNT = "Tổng tất cả bài viết"

    ACTIVITY_TITLE = "Tiêu đề mục hoạt động"
    MONTH_COL = "Cột tháng"


class DialogMsg:
    BTN_SELECT_ALL = "Nút chọn tất cả các trường"
    BTN_DESELECT_ALL = "Nút bỏ chọn tất cả các trường"
    BTN_POST_SELECT_ALL = "Nút chọn tất cả các trường bài viết"
    BTN_POST_DESELECT_ALL = "Nút bỏ chọn tất cả các trường bài viết"
    BTN_CANCEL = "Nút hủy"
    BTN_EXPORT = "Nút xuất"

    LABEL = "Trường {name}"

    FILE_FOUND = "Tìm thấy file {file_name}"
    FILE_NOT_FOUND = "Không tìm thấy file {file_name}"

    FIELD_SUMMARY_HEADER = "Tiêu để bảng tóm tắt"
    FIELD_SUMMARY_DATA = "Giá trị trong bảng tóm tắt"

    POST_DETAIL_HEADER = "Tiêu đề bảng chi tiết bài viết"
    POST_DETAIL_DATA = "Nội dung bài viết"

    FIELD_USER_ID = "Trường id người dùng"
    FIELD_USERNAME = "Trường tên đăng nhập"
    FIELD_DISPLAY_NAME = "Trường tên hiển thị"
    FIELD_TOTAL_POST = "Trường tổng số bài viết"
    FIELD_AVG_WORD = "Trường số từ / bài"
    FIELD_APPROVAL_RATE = "Trường tỉ lệ duyệt"

    COLUMN = "Cột {name}"

class AdminHomeMsg:
    ADMIN_HOME = "Trang chủ admin"
    HOME_TITLE = "Tiêu đề trang chủ"
    BTN_LOGOUT = "Nút đăng xuất"
    POST_MANAGE_CARD_TITLE = "Tiêu đề thẻ quản lý bài viết"
    POST_MANAGE_CARD_DESC = "Mô tả thẻ quản lý bài viết"

    BTN_ACCESS = "Nút truy cập"
    BTN_HOME = "Nút trang chủ"
    BTN_POST_MANAGE = "Nút trang quản lý bài viết"


class PostManageMsg:
    POST_STATISTICS_TITLE = "Tiêu đề mục thống kê bài viết"
    POST_STATUS_TITLE = "Tiêu đề mục tỉ lệ trạng thái"
    POST_PENDING_LIST = "Tiêu đề mục danh sách bài viết chờ"

    POST_HEADER = "Tiêu đề cột bảng"
    RATIO_ATTRIBUTE = "Thuộc tính tỉ lệ"

    OPTION_TYPE = "Lựa chọn {name}"
    TIME_CASE = "Danh sách lựa chọn"

    STATUS_OPTION = "Lựa chọn trạng thái"

    PENDING_LIST_COUNT = "Số lượng bài viết trong danh sách chờ"
    POST_TITLE = "Tiêu đề bài viết"



# from enum import Enum, auto
#
#
# class TC1_LOGIN(Enum):
#     STATUS = auto()
#     URL_PATH = auto()
#
#
# class TC2_LOGIN_FAIL(Enum):
#     STATUS = auto()
#
#
# class TC3_LOGOUT(Enum):
#     STATUS = auto()
#
#
# class TC4_CREATE_POST(Enum):
#     STATUS = auto()
#     POST_TITLE = auto()
#     BADGE_APPROVE = auto()
#     BADGE_PUBLIC = auto()
#     BADGE_PUBLISH = auto()
#
#
# TEST_CASE_DATA = {
#     "TC1": [
#         (TC1_LOGIN.STATUS, "Mã trạng thái", "200"),
#         (TC1_LOGIN.URL_PATH, "Đường dẫn sau khi đăng nhập", "/home"),
#     ],
#     "TC2": [
#         (TC2_LOGIN_FAIL.STATUS, "Mã trạng thái", "404")
#     ],
#     "TC3": [
#         (TC3_LOGOUT.STATUS, "Mã trạng thái", "401")
#     ],
#     "TC4": [
#         (TC4_CREATE_POST.STATUS, "Mã trạng thái", "201"),
#         (TC4_CREATE_POST.POST_TITLE, "Tiêu đề bài viết", "{post_title}"),
#         (TC4_CREATE_POST.BADGE_APPROVE, "Trạng thái bài viết", "{post_status}"),
#         (TC4_CREATE_POST.BADGE_PUBLIC, "Trạng thái công khai", "{post_public}"),
#         (TC4_CREATE_POST.BADGE_PUBLISH, "Trạng thái xuất bản", "{post_publish}")
#     ],
#     "TC6": [
#         ("ML_LOGOUT_BTN", "Tiêu đề Nút Đăng xuất", "Đăng xuất"),
#         ("ML_POST_CARD_TITLE", "Tiêu đề Thẻ QLBV", "Quản lý bài viết"),
#         ("ML_POST_CARD_DESC", "Mô tả Thẻ QLBV", "Tạo và chỉnh sửa nội dung."),
#         # ...
#     ],
#     # ...
# }
#
#
# def get_expected_items(test_case_id: str) -> list:
#     return TEST_CASE_DATA.get(test_case_id, [])
