from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from blog.posts.model import PostStatus


class Range(BaseModel):
    start: str
    end: str


class PostCount(BaseModel):
    label: str
    total: Optional[int] = 0


class PostStats(BaseModel):
    type: str
    range: Range
    stats: List[PostCount]


class PostStatusCount(BaseModel):
    total: Optional[int] = 0
    approve: Optional[int] = 0
    pending: Optional[int] = 0
    reject: Optional[int] = 0


class ExportReportRequest(BaseModel):
    user_id: int
    summary_fields: List[str]
    post_fields: List[str]


class PostDetailReport(BaseModel):
    id: Optional[int]
    title: Optional[str]
    content: Optional[str]
    summary: Optional[str]
    user_id: Optional[int]
    published: Optional[bool]
    is_public: Optional[bool]
    status: Optional[PostStatus]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

