import io
import re
from datetime import datetime
from typing import Optional

import pandas as pd
from flask import send_file, make_response
from sqlalchemy import func, and_, String, cast, case, distinct, extract, desc

from blog import db
from blog.exception import NotFound
from blog.posts.model import PostStatus, Posts
from blog.report.schema import PostStats, Range, PostCount, PostStatusCount, ExportReportRequest
from blog.users import Users

available_summary_fields = (
    "user_info",
    "total_posts",
    "avg_length",
    "approval_rate",
    "export_posts"
)

post_fields_map = {
    "id": "id",
    "title": "title",
    "content": "content",
    "summary": "summary",
    "user_id": "user_id",
    "published": "published",
    "is_public": "is_public",
    "status": "status",
    "created_at": "created_at",
    "updated_at": "updated_at",
}


class ReportService:
    @classmethod
    def get_post_stats(cls, type_: str, start_date: datetime, end_date: datetime, status: Optional[PostStatus] = None, user_id: Optional[int] = None):
        end_date = datetime.combine(end_date.date(), datetime.max.time())
        start_date = datetime.combine(start_date.date(), datetime.min.time())

        filters = [Posts.created_at.between(start_date, end_date)]
        if status:
            filters.append(Posts.status == status)

        if user_id:
            filters.append(Posts.user_id == user_id)

        if type_ == "daily":
            label_expr = func.date(Posts.created_at)
        elif type_ == "weekly":
            label_expr = func.concat(
                func.extract("year", Posts.created_at),
                "-W",
                func.extract("week", Posts.created_at)
            )
        elif type_ == "monthly":
            label_expr = func.concat(
                func.extract("year", Posts.created_at),
                "-",
                func.lpad(cast(func.extract("month", Posts.created_at), String), 2, "0")
            )
        elif type_ == "yearly":
            label_expr = func.extract("year", Posts.created_at)

        query = (
            db.session.query(label_expr.label("label"), func.count().label("total"))
            .filter(and_(*filters))
            .group_by("label")
            .order_by("label")
        )

        results = query.all()
        # data = [{"label": str(row.label), "total": row.total} for row in results]
        response = PostStats(
            type=type_,
            range=Range(
                start=start_date.date().isoformat(),
                end=end_date.date().isoformat(),
            ),
            stats=[PostCount(
                label=str(row.label),
                total=row.total
            )
                for row in results
            ]
        )

        return response

    @classmethod
    def status_report(cls, user_id: int = None, is_public: bool = True):
        query = (
            db.session.query(
                func.count(Posts.id).label('total'),
                func.count(case((Posts.status == 'approve', 1))).label('approve'),
                func.count(case((Posts.status == 'pending', 1))).label('pending'),
                func.count(case((Posts.status == 'reject', 1))).label('reject'),
            )
            .filter(and_(Posts.published.is_(True), Posts.is_public.is_(is_public)))
        )
        if user_id:
            query = query.filter(Posts.user_id == user_id)

        row = query.one()
        return PostStatusCount(
            total=row.total,
            approve=row.approve,
            pending=row.pending,
            reject=row.reject,
        )

    @classmethod
    def get_post_years(cls, user_id: int):
        query = (db.session.query(distinct(extract('year', Posts.created_at)).label('year'))
                 .filter(Posts.user_id==user_id)
                 .order_by(desc('year'))
                 .all())
        years = [y[0] for y in query]

        return years

    @classmethod
    def export(cls, export: ExportReportRequest):
        user_id = export.user_id

        user = Users.query.get(user_id)
        if not user:
            raise NotFound(message="User not found.")

        summary_fields = export.summary_fields
        post_fields = export.post_fields

        summary_data = []
        post_data = []

        post_status = cls.status_report(user_id)
        posts = Posts.query.filter_by(user_id=user_id).all()

        summary_row = {}
        for field in summary_fields:
            if field in available_summary_fields:
                if field == "user_info":
                    summary_row['User ID'] = user.id
                    summary_row['Username'] = user.username
                    summary_row['Display name'] = user.display_name

                if field == "total_posts":
                    summary_row['Total post'] = post_status.total

                if field == "avg_length":
                    total_words = sum(len(post.content.split()) for post in posts)
                    avg_words = total_words // len(posts) if posts else 0
                    summary_row['Average words'] = f"{avg_words}"

                if field == "approval_rate":
                    rate = (post_status.approve * 100 / post_status.total) if post_status.total else 0
                    summary_row['Approval rate'] = f"{rate:.2f}%"

                if field == "export_posts":
                    for post in posts:
                        post_row = {}
                        for p_field in post_fields:
                            if hasattr(post, post_fields_map.get(p_field, "")):
                                post_row[p_field] = getattr(post, p_field)
                        post_data.append(post_row)
        summary_data.append(summary_row)

        df_post = pd.DataFrame(post_data)
        df_summary = pd.DataFrame(summary_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_username = re.sub(r"[^\w\d-]", "_", user.username)
        filename = f"report_{safe_username}_{timestamp}.xlsx"
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            if not df_post.empty:
                df_post.to_excel(writer, sheet_name="Posts", index=False)

        output.seek(0)
        response = make_response(send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        ))
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response
        # return send_file(
        #     output,
        #     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #     as_attachment=True,
        #     download_name=filename,
        # )

    #
    # @classmethod
    # def get_avg_length(cls, user_id):
    #     posts = Posts.query.filter(user_id=user_id).all()
    #     total_words = sum(len(post["content"].split()) for post in posts)
    #     avg_words = total_words // len(posts) if posts else 0
    #
    #     return avg_words





