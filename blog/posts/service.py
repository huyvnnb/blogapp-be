from typing import Optional

from sqlalchemy import func, Float, cast

from blog import db
from blog.base.service import CRUDTemplate
from blog.exception import NotFound, Forbidden
from blog.posts.model import Posts, PostStatus
from blog.posts.schema import Article, Author, PostSchema, PostResponse, PostCreateRequest, PostCreateResponse, \
    PublicPostResponse, PrivatePostResponse, PublicArticleResponse, UpdatePostRequest, UpdatePostResponse, PostSearch, \
    PostSearchResponse, Cursor
from blog.users.model import Users


class PostService(CRUDTemplate):
    model = Posts

    @classmethod
    def create_post(cls, user_id: int, post: PostCreateRequest):
        new_post = Posts(
            title=post.title,
            summary=post.summary,
            content=post.content,
            published=post.published,
            is_public=post.is_public,
            status=PostStatus.PENDING,
            user_id=user_id
        )
        db.session.add(new_post)
        db.session.commit()
        db.session.refresh(new_post)

        return PostCreateResponse.from_entity(new_post)

    @classmethod
    def update_post(cls, user_id: int, post_id: int, post: UpdatePostRequest):
        existing_post = Posts.query.filter_by(id=post_id).first()

        if not existing_post:
            raise NotFound("Post not found.")

        if existing_post.user_id != user_id:
            raise Forbidden("You are not allowed to edit this post.")

        existing_post.title = post.title
        existing_post.summary = post.summary
        existing_post.content = post.content
        existing_post.is_public = post.is_public
        existing_post.published = post.published

        existing_post.status = PostStatus.PENDING

        db.session.commit()

        return UpdatePostResponse.from_entity(existing_post)

    @classmethod
    def get_post_by_id(cls, id: int, current_user: Optional[Users]):
        post = Posts.query.filter_by(id=id).first()
        if not post:
            raise NotFound(message="Post not found")

        is_owner = current_user and current_user.id == post.user_id

        if not post.is_public or not post.published or post.status != PostStatus.APPROVE:
            if not is_owner:
                raise Forbidden("You do not have permission to view this post")

            return PrivatePostResponse.from_entity(post)

        if is_owner:
            return PrivatePostResponse.from_entity(post)

        return PublicPostResponse.from_entity(post)

    @classmethod
    def get_public_post_by_id(cls, id: int):
        post = (Posts.query.filter_by(
            id=id,
            published=True,
            is_public=True,
            status=PostStatus.APPROVE
        ).join(Users, Users.id == Posts.user_id).first())
        if not post:
            raise NotFound(message="Post not exist.")

        response = PublicPostResponse.from_entity(post)
        return response

    @classmethod
    def get_private_post_by_id(cls, post_id):
        post = Posts.query.filter_by(id=post_id).first()
        if not post:
            raise NotFound(message="Post not exist.")

        response = PrivatePostResponse.from_entity(post)
        return response

    # @classmethod
    # def get_articles(cls):
    #     articles = (db.session.query(Posts, Users.id, Users.username)
    #                 .join(Users)
    #                 .filter(Posts.published == True)
    #                 .all()
    #                 )
    #
    #     results = []
    #     for post, user_id, username in articles:
    #         article = Article(
    #             id=post.id,
    #             title=post.title,
    #             summary=post.summary or post.content[:100] + '...',
    #             created_at=post.created_at,
    #             author=Author(
    #                 id=user_id,
    #                 username=username
    #             )
    #         )
    #         results.append(article.model_dump())
    #
    #     return results

    @classmethod
    def get_public_post_by_user_id(
            cls,
            user_id,
    ):
        posts = (
            db.session.query(Posts)
            .filter(
                Posts.user_id == user_id,
                Posts.published == True,
                Posts.is_public == True,
                Posts.status == PostStatus.APPROVE
            )
            .order_by(Posts.created_at.desc())
            .all()
        )

        result = [
            PublicPostResponse.from_entity(post)
            for post in posts
        ]
        return result

    @classmethod
    def get_public_article_by_user_id(cls, user_id):
        posts = (
            db.session.query(Posts)
            .filter(
                Posts.user_id == user_id,
                Posts.published == True,
                Posts.is_public == True,
                Posts.status == PostStatus.APPROVE
            )
            .order_by(Posts.created_at.desc())
            .all()
        )

        result = [
            PublicArticleResponse.from_entity(post)
            for post in posts
        ]
        return result

    @classmethod
    def get_private_article_by_user_id(cls, user_id):
        posts = (
            db.session.query(Posts)
            .filter(Posts.user_id == user_id)
            .order_by(Posts.created_at.desc())
            .all()
        )

        result = [
            PrivatePostResponse.from_entity(post)
            for post in posts
        ]
        return result

    @classmethod
    def delete_post(cls, user_id, post_id: int):
        post = Posts.query.filter(Posts.id == post_id).first()
        if not post:
            raise NotFound("Post not found")

        if user_id != post.user_id:
            raise Forbidden("You cannot delete this post.")

        db.session.delete(post)
        db.session.commit()

    @classmethod
    def search_post(cls, query: str, limit: int = 10, last_rank: float = None, last_id: int = None,
                    rank_threshold: float = 0.02):
        unaccented_query = func.unaccent(query)
        tsquery = func.to_tsquery('simple', func.replace(unaccented_query, ' ', '|'))

        # Posts.search_vector = (
        #         func.setweight(func.to_tsvector('simple', func.unaccent(func.coalesce(Posts.title, ''))), 'A') +
        #         func.setweight(func.to_tsvector('simple', func.unaccent(func.coalesce(Posts.summary, ''))), 'B') +
        #         func.setweight(func.to_tsvector('simple', func.unaccent(func.coalesce(Posts.content, ''))), 'C')
        # )
        rank_expr = func.ts_rank(Posts.search_vector, tsquery)
        epsilon = 1e-4

        q = Posts.query.add_columns(rank_expr.label('rank')).filter(
            Posts.search_vector.op("@@")(tsquery),
            Posts.status == PostStatus.APPROVE,
            rank_expr >= rank_threshold
        )
        if last_rank is not None and last_id is not None:
            q = q.filter(
                (rank_expr < last_rank - epsilon)
                | (func.abs(rank_expr - last_rank) < epsilon) & (Posts.id < last_id)
            )

        q = q.order_by(rank_expr.desc(), Posts.id.desc()).limit(limit)
        results = q.all()

        response = None
        if results:
            posts = []
            for p, rank in results:
                post = PostSearch.from_entity(p)
                post.rank = rank
                posts.append(post)

            last_rank = results[-1][1]
            last_id = results[-1][0].id

            has_more = len(results) == limit

            response = PostSearchResponse(
                posts=posts,
                cursor=Cursor(
                    last_rank=last_rank,
                    last_id=last_id
                ),
                has_more=has_more
            )

        return response

    #
    # @classmethod
    # def get_my_post(cls, user_id: int):
    #     posts = (
    #         db.session.query(Posts)
    #         .filter(Posts.user_id == user_id)
    #         .order_by(Posts.created_at.desc())
    #         .all()
    #     )
    #
    #     result = [
    #         MyPostResponse(
    #             id=post.id,
    #             title=post.title,
    #             summary=post.summary or (post.content[:100] + "..."),
    #             content=post.content,
    #             is_public=post.is_public,
    #             published=post.published,
    #             status=post.status,
    #             created_at=post.created_at,
    #             updated_at=post.updated_at,
    #         )
    #         for post in posts
    #     ]
    #     return result
