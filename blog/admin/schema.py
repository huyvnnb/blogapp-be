from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from blog.posts import Posts
from blog.posts.model import PostStatus
from blog.users import Users


class UserPrivateResponse(BaseModel):
    id: int
    username: str
    display_name: str

    @classmethod
    def from_entity(cls, user: "Users"):
        if user is None:
            return None
        return cls(
            id=user.id,
            username=user.username,
            display_name=user.display_name
        )


class UserCreateRequest(BaseModel):
    username: str
    password: str
    display_name: str


class UpdateUserRequest(BaseModel):
    display_name: str

    @staticmethod
    def from_entity(cls, user: "Users"):
        return cls(
            display_name=user.display_name
        )


class UpdatePostStatusRequest(BaseModel):
    status: PostStatus


class AdminArticleResponse(BaseModel):
    id: int
    title: str
    author_id: int
    author_name: str
    status: PostStatus
    created_at: datetime

    @staticmethod
    def from_entity(post: "Posts"):
        return AdminArticleResponse(
            id=post.id,
            title=post.title,
            author_id=post.user_id,
            author_name=getattr(post.user, "username", "Unknown"),
            status=post.status,
            created_at=post.created_at,
        )


class AdminPostResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    content: str
    author_id: int
    author_name: str
    status: PostStatus
    created_at: datetime

    @staticmethod
    def from_entity(post: "Posts"):
        return AdminPostResponse(
            id=post.id,
            title=post.title,
            summary=post.summary,
            content=post.content,
            author_id=post.user_id,
            author_name=getattr(post.user, "username", "Unknown"),
            status=post.status,
            created_at=post.created_at,
        )


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminResponse(BaseModel):
    id: int
    username: str
    display_name: str


class AdminLoginResponse(BaseModel):
    token: str
    user: AdminResponse
