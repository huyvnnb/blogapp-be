baseUrl = "http://localhost:5173"


class Auth:
    LOGIN = f"{baseUrl}/login"
    LOGOUT = f"{baseUrl}/logout"
    HOME = f"{baseUrl}/home"


class Post:
    NEW_POST = f"{baseUrl}/posts/new"

    @staticmethod
    def post_detail(post_id: str):
        return f"{baseUrl}/posts/{post_id}"


class User:
    @staticmethod
    def user_posts(user_id: str):
        return f"{baseUrl}/users/{user_id}/posts"


class Dashboard:
    DASHBOARD = f"{baseUrl}/dashboard"


class Admin:
    LOGIN = f"{baseUrl}/admin/login"
    HOME = f"{baseUrl}/admin"
    POST_MANAGE = f"{baseUrl}/admin/posts"
