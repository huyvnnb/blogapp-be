import random
from datetime import timedelta, datetime

from blog import db, create_app
from blog.posts.model import PostStatus
from blog.users import Users, Role, Permission
from blog.posts import Posts, Comment

app = create_app()
app.app_context().push()


def seed_data():
    # 1. Reset DB
    db.drop_all()
    db.create_all()

    Users.query.delete()
    Role.query.delete()
    Permission.query.delete()
    Posts.query.delete()
    db.session.commit()

    perm_create_post = Permission(name="create_post")
    perm_edit_post = Permission(name="edit_post")
    perm_delete_post = Permission(name="delete_post")
    perm_view_post = Permission(name="view_post")
    db.session.add_all([perm_create_post, perm_edit_post, perm_delete_post, perm_view_post])
    db.session.commit()

    # 3. Seed Roles
    role_admin = Role(name="admin", permissions=[perm_create_post, perm_edit_post, perm_delete_post, perm_view_post])
    role_user = Role(name="user", permissions=[perm_create_post, perm_view_post])
    db.session.add_all([role_admin, role_user])
    db.session.commit()

    # 4. Seed Users
    user1 = Users(username="huy", display_name="Huy Nguyen", roles=[role_admin])
    user1.set_password("password")

    user2 = Users(username="linh", display_name="Linh Tran", roles=[role_user])
    user2.set_password("password")

    db.session.add_all([user1, user2])
    db.session.commit()

    users = []
    for i in range(1, 11):
        username = f"user{i}"
        display_name = f"User {i}"
        user = Users(username=username, display_name=display_name, roles=[role_user])
        user.set_password("password")
        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    # 5. Seed Posts
    statuses = [PostStatus.APPROVE, PostStatus.PENDING, PostStatus.REJECT]

    def random_date(start, end):
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    # Sinh dữ liệu demo
    titles = ["Hello World", "Second Post", "Sample Post", "Test Post", "Demo Post"]
    contents = [
        "Đây là nội dung bài viết mẫu để thử nghiệm FTS tiếng Việt.",
        "Một bài viết khác để kiểm tra chức năng tìm kiếm và ranking.",
        "Nội dung dài hơn để kiểm tra việc tạo search_vector và index GIN.",
        "Bài viết demo với nội dung ngẫu nhiên, có thể chứa nhiều từ khóa khác nhau.",
    ]

    summaries = [
        "Tóm tắt ngắn gọn 1",
        "Tóm tắt ngắn gọn 2",
        "Demo summary",
        "Bài viết thử nghiệm",
    ]

    # Khoảng thời gian: từ 01/01/2023 đến 30/09/2025
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 9, 30)

    posts = []

    for i in range(100):
        title = random.choice(titles) + f" #{i + 1}"
        content = random.choice(contents)
        summary = random.choice(summaries)
        user_id = random.randint(1, 12)
        status = random.choice(statuses)
        published = random.choice([True, False])
        is_public = random.choice([True, False])
        created_at = random_date(start_date, end_date)
        updated_at = created_at + timedelta(days=random.randint(0, 30))  # updated sau created

        post = Posts(
            title=title,
            content=content,
            summary=summary,
            user_id=user_id,
            status=status,
            published=published,
            is_public=is_public,
            created_at=created_at,
            updated_at=updated_at
        )

        from sqlalchemy import func
        post.search_vector = db.session.execute(
            func.to_tsvector('simple', func.unaccent(title + " " + content + " " + (summary or "")))
        ).scalar()

        posts.append(post)

    db.session.add_all(posts)
    db.session.commit()
    print("Seed data completed!")


if __name__ == "__main__":
    seed_data()
