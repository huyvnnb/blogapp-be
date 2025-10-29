from typing import Any

from flask import request
from sqlalchemy import func

from blog import db
from blog.base.service import CRUDTemplate
from blog.exception import NotFound, Unauthorized, ApiError, ServerError
from blog.posts import Posts
from blog.posts.model import PostStatus
from blog.users.model import Users, Role
from blog.users.schema import UserCreate, UserLogin, LoginResponse, UserResponse, UserRegister, RefreshRequest, \
    RefreshResponse, UserEffective, UserPublicResponse
from blog.utils.helper import get_password_hash, verify_password, create_access_token, verify_refresh_token, \
    create_refresh_token


class UserService(CRUDTemplate):
    model = Users

    @classmethod
    def create_user(cls, user_in: UserCreate):
        user = _prepare_user_data(user_in)

        db.session.add(user)
        db.session.commit()
        return UserResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name
        )

    @classmethod
    def get_by_username(cls, username: str):
        existed_user = Users.query.filter(Users.username == username).first()

        return existed_user

    @classmethod
    def get_public_user_info(cls, username: str):
        existed_user = Users.query.filter(Users.username == username)
        if not existed_user:
            raise NotFound(message=f"User '{username}' not exist.")

        return UserPublicResponse.from_entity(existed_user)

    @classmethod
    def get_most_effective_users(cls, top: int = 10):
        results = (
            (db.session.query(
                Users,
                func.count(Posts.id).label("total_posts"),
            ).join(Posts, Posts.user_id == Users.id, isouter=True)).filter(Posts.status==PostStatus.APPROVE)
            .group_by(Users.id)
            .order_by(func.count(Posts.id).desc())
            .limit(top).all()
        )

        response = [UserEffective(
            user_id=u.id,
            username=u.username,
            display_name=u.display_name,
            total_posts=total_posts
        ) for u, total_posts in results]

        return response


class AuthService:
    @classmethod
    def register(cls, user_in: UserRegister):
        existed_user = UserService.get_by_username(user_in.username)
        if existed_user:
            raise ApiError(message="Account existed")

        user = Users(
            username=user_in.username,
            display_name=user_in.display_name,
        )

        default_role = _get_default_role()
        if default_role:
            user.roles.append(default_role)

        hash_password = get_password_hash(user_in.password)
        user.hashed_password = hash_password

        db.session.add(user)
        db.session.commit()

    @classmethod
    def login(cls, user_in: UserLogin):
        existed_user = UserService.get_by_username(user_in.username)
        if not existed_user:
            raise NotFound(message="Account not exist")

        verified = verify_password(user_in.password, existed_user.hashed_password)

        if not verified:
            raise Unauthorized(message="Username or password not correct.")

        data = {"user_id": existed_user.id}

        token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        return LoginResponse(
            token=token,
            user=UserResponse(
                id=existed_user.id,
                username=existed_user.username,
                display_name=existed_user.display_name
            )
        ), refresh_token

    @classmethod
    def refresh_token(cls):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise Unauthorized("Missing refresh token")

        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            raise Unauthorized("Invalid or expired refresh token")

        new_access_token = create_access_token({'user_id': user_id})

        return RefreshResponse(
            token=new_access_token
        )


def _check_user_existence(username: str):
    existed_user = UserService.get_by_username(username)
    if existed_user:
        raise ApiError(message="Account existed")
    return False


def _get_default_role():
    default_role = Role.query.filter(Role.name == 'user').first()
    if not default_role:
        raise ServerError(message="Default role must be initialize before startup.")

    return default_role


def _prepare_user_data(user_in: Any):
    user = Users()
    if hasattr(user_in, "username"):
        user.username = user_in.username
    if hasattr(user_in, "display_name"):
        user.display_name = user_in.display_name
    if hasattr(user_in, "password"):
        hashed_pw = get_password_hash(user_in.password)
        user.hashed_password = hashed_pw

    return user


