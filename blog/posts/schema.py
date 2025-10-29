from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from blog.posts import Posts
from blog.posts.model import PostStatus
from blog.users.schema import UserResponse


class PostCreateRequest(BaseModel):
    title: str = Field(max_length=100, min_length=1)
    content: str = Field(min_length=1)
    summary: Optional[str] = Field(..., max_length=300)
    published: Optional[bool] = False
    is_public: Optional[bool] = False


class PostCreateResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str]
    published: Optional[bool]
    is_public: Optional[bool]
    status: Optional[PostStatus] = PostStatus.PENDING
    created_at: datetime
    user_id: int

    @staticmethod
    def from_entity(post: "Posts") -> "PostCreateResponse":
        return PostCreateResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            summary=post.summary,
            published=post.published,
            is_public=post.is_public,
            status=post.status,
            created_at=post.created_at,
            user_id=post.user_id,
        )


class PostSchema(BaseModel):
    title: str
    content: str
    summary: Optional[str]
    published: bool
    user_id: int


class Author(BaseModel):
    id: int
    username: str

    @classmethod
    def from_entity(cls, user):
        if not user:
            return None
        return cls(
            id=user.id,
            username=user.username,
        )


class PostResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    content: str
    is_public: bool
    published: bool
    status: PostStatus
    created_at: datetime
    author: Author


class Article(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    created_at: datetime
    author: Author


class PublicPostResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    content: str
    created_at: datetime
    author: Author

    @staticmethod
    def from_entity(post: "Posts") -> "PublicPostResponse":
        return PublicPostResponse(
            id=post.id,
            title=post.title,
            summary=post.summary or (post.content[:100] + "..."),
            content=post.content,
            created_at=post.created_at,
            author=Author(
                id=post.user.id,
                username=post.user.username,
            ),
        )


class PrivatePostResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    content: str
    is_public: bool
    published: bool
    status: PostStatus
    created_at: datetime
    author: Author

    @staticmethod
    def from_entity(post: "Posts") -> "PrivatePostResponse":
        return PrivatePostResponse(
            id=post.id,
            title=post.title,
            summary=post.summary or (post.content[:100] + "..."),
            content=post.content,
            is_public=post.is_public,
            published=post.published,
            status=post.status,
            created_at=post.created_at,
            author=Author(
                id=post.user.id,
                username=post.user.username,
            )
        )


class PrivateArticleResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    created_at: datetime
    is_public: bool
    published: bool
    status: PostStatus

    @classmethod
    def from_entity(cls, post: "Posts"):
        return cls(
            id=post.id,
            title=post.title,
            summary=post.summary or (post.content[:100] + "..."),
            is_public=post.is_public,
            published=post.published,
            status=post.status,
            created_at=post.created_at,
        )


class PublicArticleResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    created_at: datetime
    author: Author

    @classmethod
    def from_entity(cls, post: "Posts"):
        return cls(
            id=post.id,
            title=post.title,
            summary=post.summary or (post.content[:100] + "..."),
            created_at=post.created_at,
            author=Author.from_entity(post.user) if hasattr(post, "user") else None,
        )


class UpdatePostRequest(BaseModel):
    title: str
    summary: Optional[str]
    content: str
    is_public: bool
    published: bool


class UpdatePostResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    content: str
    is_public: bool
    published: bool
    status: Optional[PostStatus] = PostStatus.PENDING
    created_at: datetime

    @staticmethod
    def from_entity(post: "Posts") -> "UpdatePostResponse":
        return UpdatePostResponse(
            id=post.id,
            title=post.title,
            summary=post.summary,
            content=post.content,
            is_public=post.is_public,
            published=post.published,
            status=post.status,
            created_at=post.created_at,
        )


class Cursor(BaseModel):
    last_rank: float
    last_id: int


class PostSearch(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    created_at: datetime
    user_id: int
    username: str
    rank: Optional[float] = 0

    @staticmethod
    def from_entity(post: "Posts") -> "PostSearch":
        return PostSearch(
            id=post.id,
            title=post.title,
            summary=post.summary or post.content[:100],
            created_at=post.created_at,
            user_id=post.user_id,
            username=post.user.username
        )


class PostSearchResponse(BaseModel):
    posts: List[PostSearch]
    cursor: Optional[Cursor]
    has_more: Optional[bool] = False

