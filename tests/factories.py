import time
import uuid
from datetime import datetime
from typing import Optional

import pytest
from sqlalchemy.orm import Session

from blog.posts import Posts
from blog.users import Role, Users
from blog.utils.helper import get_password_hash


class TestDataFactory:
    def __init__(self, session):
        self.session = session
        self.created_objects = []

    def create_role(self, name=None):
        name = name or f"role_{uuid.uuid4().hex[:6]}"
        role = Role(name=name)
        self.session.add(role)
        self.session.commit()
        self.created_objects.append(role)
        return role

    def create_user(self, role_id, username=None, password="password"):
        role = self.session.get(Role, role_id)
        username = username or f"user_{uuid.uuid4().hex[:6]}"
        hashed = get_password_hash(password)
        user = Users(
            username=username,
            hashed_password=hashed,
            display_name=f"User {username}",
            roles=[role],
        )
        self.session.add(user)
        self.session.commit()
        self.created_objects.append(user)
        return user, password

    def create_post(self, user, **kwargs):
        defaults = {
            "title": f"Post {int(time.time())}",
            "content": "Default post content",
            "status": "APPROVE",
            "is_public": True,
            "published": True,
            "user_id": user.id,
        }
        defaults.update(kwargs)
        post = Posts(**defaults)
        self.session.add(post)
        self.session.commit()
        self.created_objects.append(post)
        return post

    def create_posts(self, user, title_pref: str, summary: str, content: str, count: int = 10, **kwargs):
        posts = []
        for i in range(count):
            uid = str(uuid.uuid4())[:8]
            post = Posts(
                title=f"{title_pref} - {uid}",
                summary=summary,
                content=f"{content} - {uid}",
                status=kwargs.get("status", "APPROVE"),
                is_public=kwargs.get("is_public", True),
                published=kwargs.get("published", True),
                user_id=user.id
            )
            posts.append(post)

        self.session.add_all(posts)
        self.session.commit()
        self.created_objects.extend(posts)
        return posts

    def cleanup(self):
        for obj in reversed(self.created_objects):
            try:
                self.session.delete(obj)
            except Exception:
                pass
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
        self.created_objects.clear()