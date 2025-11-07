from flask import Blueprint, request, make_response

from blog.exception import NotFound
from blog.posts.service import PostService
from blog.users import Users
from blog.users.schema import UserCreate, UserRegister, Me, UserLogin, UserResponse, RefreshRequest, UserPublicResponse
from blog.users.service import UserService, AuthService
from blog.utils.helper import get_password_hash, token_require, get_token_jti, get_jwt_token
from blog.utils.response import success
import logging

logger = logging.getLogger()
user_bp = Blueprint("users", __name__, url_prefix="/users")
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# @user_bp.route("/", methods=["GET"])
# def get_all_users():
#     data = UserService.get_all()
#     return success(data=data, message="Get users list successfully.")


@user_bp.route("/<int:id>/", methods=["GET"])
def get_user_by_id(id: int):
    existing_user = Users.query.get(id)
    if not existing_user:
        raise NotFound("User not found")

    response = UserPublicResponse(
        id=existing_user.id,
        username=existing_user.username,
        display_name=existing_user.display_name
    )
    return success(data=response, message="Get user successfully")


@user_bp.route("/<string:username>/", methods=["GET"])
def get_public_info(username: str):
    response = UserService.get_public_user_info(username)

    return success(data=response, message="Get user's public info successfully.")


# @user_bp.route("/", methods=["POST"])
# def create_user():
#     data = UserCreate(**request.get_json())
#     response = UserService.create_user(data)
#     return success(data=data, message="Create user successfully.")


@user_bp.route("/<int:user_id>/posts")
@token_require
def get_post_by_user_id(user_id: int):
    data = PostService.get_public_post_by_user_id(user_id)
    return success(data=data, message=f"Get post of user {user_id} successfully")


@user_bp.route("/me", methods=["GET"])
@token_require
def get_me(user: Me):
    return success(data=user, message="Get profile successfully")


@user_bp.route("/me/posts", methods=["GET"])
@token_require
def get_my_post(user: Me):
    response = PostService.get_private_article_by_user_id(user.user_id)
    return success(data=response, message="Get articles successfully")


@user_bp.route("/effective", methods=["GET"])
def get_effective_users():
    top = request.args.get("top", default=10, type=int)
    response = UserService.get_most_effective_users(top)

    return success(data=response, message="Get users list successfully.")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = UserLogin(**request.get_json())
    data, refresh_token = AuthService.login(data)
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
    # return success(data=response, message="Login successfully")


@auth_bp.route("/logout", methods=["POST"])
@token_require
def logout(user):
    resp = success(message="Logout successfully")
    response = make_response(resp)
    response.delete_cookie('refresh_token')
    token = get_jwt_token()
    jti = get_token_jti(token)
    logger.info(f"Revoked token with jti: {jti}")
    AuthService.revoke_token(jti)
    return response

# @auth_bp.route("/logout", methods=["POST"])
# @token_require
# def logout(user):
#     resp = success(message="Logout successfully")
#     response = make_response(resp)
#     response.delete_cookie('refresh_token')
#
#     return response


@auth_bp.route("/register", methods=["POST"])
def register():
    data = UserRegister(**request.get_json())
    AuthService.register(data)

    return success(message="Register successfully.")


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    response = AuthService.refresh_token()
    return success(data=response, message="New token created successfully.")
