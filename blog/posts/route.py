from flask import Blueprint, request

from blog.exception import Forbidden
from blog.posts.schema import PostSchema, PostCreateRequest, UpdatePostRequest, PostSearchResponse
from blog.posts.service import PostService
from blog.users.schema import Me
from blog.utils.helper import token_require, get_current_user
from blog.utils.response import success

post_bp = Blueprint("posts", __name__, url_prefix="/posts")


@post_bp.route("/<int:id>/", methods=["GET"])
def get_post_by_id(id: int):
    current_user = get_current_user()
    response = PostService.get_post_by_id(id, current_user)

    return success(data=response, message="Get post successfully.")


# @post_bp.route("/public/<int:id>/", methods=["GET"])
# def get_public_post_by_id(id: int):
#     data = PostService.get_public_post_by_id(id)
#     return success(data=data, message="Get post successfully")
#
#
# @post_bp.route("/private/<int:id>/", methods=["GET"])
# @token_require
# def get_private_post_by_id(id: int):
#     response = PostService.get_private_post_by_id(id)
#     return success(data=response, message="Get post successfully")


@post_bp.route("/", methods=["POST"])
@token_require
def create_post(user: Me):
    data = request.get_json()
    post = PostCreateRequest(**data)

    response = PostService.create_post(user.user_id, post)
    return success(data=response, message="Create post successfully", status=201)


@post_bp.route("/articles/<int:user_id>/", methods=["GET"])
def get_public_articles(user_id):
    response = PostService.get_public_article_by_user_id(user_id)

    return success(data=response, message="Get public articles successfully.")


@post_bp.route("/articles", methods=["GET"])
@token_require
def get_private_articles(user):
    response = PostService.get_private_article_by_user_id(user.user_id)

    return success(data=response, message="Get private articles successfully.")


@post_bp.route("/<int:id>/", methods=["PUT"])
@token_require
def update_post(user: Me, id: int):
    post = UpdatePostRequest(**request.get_json())

    response = PostService.update_post(user.user_id, id, post)
    return success(data=response, message="Update post successfully")


@post_bp.route("/<int:id>/", methods=["DELETE"])
@token_require
def delete_post(user, id: int):
    response = PostService.delete_post(user.user_id, id)
    return success(data=response, message="Delete post successfully")


@post_bp.route("/search", methods=["GET"])
@token_require
def search_posts(user):
    query = request.args.get("query", "")
    limit = int(request.args.get("limit", 10))
    last_rank = request.args.get("last_rank")
    last_id = request.args.get("last_id")

    last_rank = float(last_rank) if last_rank is not None else None
    last_id = int(last_id) if last_id is not None else None

    response = PostService.search_post(query=query, limit=limit, last_rank=last_rank, last_id=last_id)

    if response:
        return success(data=response, message="Search posts successfully.")

    return success(data=PostSearchResponse(posts=[], cursor=None), message="Nothing more")


# @post_bp.route("/articles/", methods=["GET"])
# @token_require
# def get_articles():
#     response = PostService.get_articles()
#     return success(data=response, message="Get articles successfully")


