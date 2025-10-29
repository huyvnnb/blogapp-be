from datetime import datetime, timezone, timedelta

from flask import Blueprint, request

from blog.report.service import ReportService
from blog.utils.response import success

admin_stats_bp = Blueprint("admin_stats", __name__, url_prefix="/admin/stats")


@admin_stats_bp.route("/posts", methods=["GET"])
def get_post_stats():
    type_ = request.args.get("type", "daily")
    status = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not end_date:
        end_date = datetime.now(timezone.utc)
    else:
        end_date = datetime.fromisoformat(end_date)

    if not start_date:
        if type_ == "daily":
            start_date = end_date - timedelta(days=6)
        elif type_ == "weekly":
            start_date = end_date - timedelta(weeks=7)
        elif type_ == "monthly":
            start_date = end_date - timedelta(days=30 * 6)
        elif type_ == "yearly":
            start_date = end_date - timedelta(days=365 * 3)
        else:
            from blog import error
            return error(message="Invalid type")

    response = ReportService.get_post_stats(type_, parse_date(start_date), parse_date(end_date), status)
    return success(data=response, message="Get post stats successfully.")


@admin_stats_bp.route("/posts/status/count", methods=["GET"])
def post_status_count():
    response = ReportService.status_report()
    return success(data=response, message="Get post status count successfully.")


def parse_date(value):
    if isinstance(value, datetime):
        return value
    return datetime.strptime(value, "%Y-%m-%d")




