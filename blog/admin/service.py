from blog import db
from blog.admin.schema import UserPrivateResponse, UserCreateRequest, UpdateUserRequest, AdminArticleResponse, \
    UpdatePostStatusRequest, AdminLoginRequest, AdminLoginResponse, AdminPostResponse, AdminResponse
from blog.exception import NotFound, BadRequest, Unauthorized, Forbidden
from blog.posts import Posts
from blog.posts.model import PostStatus
from blog.users import Users
from blog.utils.helper import get_password_hash, verify_password, create_access_token, create_refresh_token


class AdminService:

    @classmethod
    def login(cls, admin: AdminLoginRequest):
        print(f"Admin: {admin}")
        existed_admin = Users.query.filter(Users.username == admin.username).first()
        print(f"User: {existed_admin}")
        if not existed_admin:
            raise NotFound(message="Account not exist")

        verified = verify_password(admin.password, existed_admin.hashed_password)

        if not verified:
            raise Unauthorized(message="Username or password not correct.")

        data = {"user_id": existed_admin.id}

        token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        roles = [role.name for role in existed_admin.roles]
        print(f"Roles: {roles}")
        is_admin = "admin" in roles
        if is_admin:
            return AdminLoginResponse(
                token=token,
                user=AdminResponse(
                    id=existed_admin.id,
                    username=existed_admin.username,
                    display_name=existed_admin.display_name
                )
            ), refresh_token
        raise Forbidden("You are not allow to login.")

    @classmethod
    def get_all_users(cls):
        users = Users.query.order_by(Users.created_at.desc()).all()

        response = [
            UserPrivateResponse.from_entity(user)
            for user in users
        ]

        return response

    @classmethod
    def get_user_by_id(cls, user_id):
        user = Users.query.filter_by(id=user_id).first()
        if not user:
            raise NotFound("User not found")
        return UserPrivateResponse.from_entity(user)

    @classmethod
    def create_user(cls, data: UserCreateRequest):
        if Users.query.filter_by(username=data.username).first():
            raise BadRequest("Username already exists")

        user = Users(
            username=data.username,
            hashed_password=get_password_hash(data.password),
            display_name=data.display_name,
        )
        db.session.add(user)
        db.session.commit()

        return UserPrivateResponse.from_entity(user)

    @classmethod
    def update_user(cls, user_id, data: UpdateUserRequest):
        user = Users.query.filter_by(id=user_id).first()
        if not user:
            raise NotFound("User not found")

        if data.display_name is not None:
            user.display_name = data.display_name

        db.session.commit()
        return UserPrivateResponse.from_entity(user)

    @classmethod
    def delete_user(cls, user_id: int):
        user = Users.query.filter_by(id=user_id).first()
        if not user:
            raise NotFound("User not found")

        db.session.delete(user)
        db.session.commit()

    @classmethod
    def get_all_pending_articles(cls):
        posts = (Posts.query.filter(
                Posts.is_public.is_(True),
                Posts.published.is_(True),
                Posts.status == PostStatus.PENDING
        ).all())

        return [
            AdminArticleResponse.from_entity(post)
            for post in posts
        ]

    @classmethod
    def update_post_status(cls, post_id: int, data: UpdatePostStatusRequest):
        post = Posts.query.filter_by(id=post_id).first()
        if not post:
            raise NotFound("Post not found")

        if data.status is not None:
            post.status = data.status

        db.session.commit()
        return AdminArticleResponse.from_entity(post)

    @classmethod
    def delete_post(cls, post_id: int):
        post = Posts.query.filter_by(id=post_id).first()
        if not post:
            raise NotFound("Post not found")

        db.session.delete(post)
        db.session.commit()

    @classmethod
    def get_post_detail(cls, post_id: int):
        post = Posts.query.filter_by(id=post_id).first()
        if not post:
            raise NotFound("Post not found")

        return AdminPostResponse.from_entity(post)
