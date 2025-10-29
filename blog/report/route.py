from datetime import datetime

from flask import Blueprint, request

from blog.report.schema import ExportReportRequest
from blog.report.service import ReportService
from blog.utils.helper import token_require
from blog.utils.response import success

user_stats_bp = Blueprint("user_stats", __name__, url_prefix="/user/stats")


@user_stats_bp.route("/posts/by-status")
@token_require
def get_post_status(user):
    response = ReportService.status_report(user.user_id)
    return success(data=response, message="Get post status successfully.")


@user_stats_bp.route("/posts/heatmap/<int:user_id>")
def get_post_heatmap(user_id):
    year = int(request.args.get("year", datetime.now().year))

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)

    report = ReportService.get_post_stats(
        type_="daily",
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )

    response = [
        {"date": stat.label, "count": stat.total}
        for stat in report.stats
    ]

    return success(data=response, message="Get user heatmap successfully.")


@user_stats_bp.route("/posts/years/<int:user_id>")
def get_posts_years(user_id: int):
    response = ReportService.get_post_years(user_id)
    return success(data=response, message="Get years successfully.")


@user_stats_bp.route("/export", methods=["POST"])
def export():
    data = ExportReportRequest(**request.get_json())

    return ReportService.export(data)
