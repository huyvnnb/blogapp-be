from flask import Blueprint, request, make_response

from blog.admin.schema import UserCreateRequest, UpdatePostStatusRequest, UpdateUserRequest, AdminLoginRequest
from blog.admin.service import AdminService
from blog.utils.helper import token_require, role_require
from blog.utils.response import success

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


@admin_bp.route("/login", methods=["POST"])
def login():
    data = AdminLoginRequest(**request.get_json())
    data, refresh_token = AdminService.login(data)
    res, _ = success(data, message="Login successfully")
    response = make_response(res, 200)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite='Strict',
        max_age=7 * 24 * 60 * 60
    )
    return response


@admin_bp.route("/users", methods=["GET"])
@token_require
@role_require("admin")
def get_all_users():
    response = AdminService.get_all_users()

    return success(data=response, message="Get user list successfully.")


@admin_bp.route("/users/<int:user_id>/", methods=["GET"])
@token_require
@role_require("admin")
def get_user_by_id(user_id: int):
    response = AdminService.get_user_by_id(user_id)

    return success(data=response, message="Get user successfully")


@admin_bp.route("/users", methods=["POST"])
@token_require
@role_require("admin")
def create_user():
    data = UserCreateRequest(**request.get_json())

    response = AdminService.create_user(data)

    return success(data=response, message="Create user successfully.")


@admin_bp.route("/users/<int:user_id>/", methods=["PUT"])
@token_require
@role_require("admin")
def update_user(user_id: int):
    data = UpdateUserRequest(**request.get_json())
    response = AdminService.update_user(user_id, data)

    return success(data=response, message="Update user successfully.")


@admin_bp.route("/posts/pending", methods=["GET"])
@token_require
@role_require("admin")
def get_all_pending_articles(user):
    response = AdminService.get_all_pending_articles()

    return success(data=response, message="Get all pending post successfully")


@admin_bp.route("/posts/<int:post_id>/", methods=["GET"])
@token_require
@role_require("admin")
def get_post_detail(user, post_id: int):
    response = AdminService.get_post_detail(post_id)
    return success(data=response, message="Get post successfully")


@admin_bp.route("/posts/<int:post_id>/status", methods=["PATCH"])
@token_require
@role_require("admin")
def update_post_status(user, post_id: int):
    data = UpdatePostStatusRequest(**request.get_json())
    response = AdminService.update_post_status(post_id, data)

    return success(data=response, message=f"Update post status to {data.status} successfully.")


@admin_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@token_require
@role_require("admin")
def delete_post(user, post_id: int):
    AdminService.delete_post(post_id)
    return success(message="Delete post successfully")
