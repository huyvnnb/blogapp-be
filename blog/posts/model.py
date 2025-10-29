import enum

from sqlalchemy import event, func, Index
from sqlalchemy.dialects.postgresql import TSVECTOR

from blog import db
from blog.base.model import ModelBase


class PostStatus(str, enum.Enum):
    APPROVE = "approve"
    PENDING = "pending"
    REJECT = "reject"


class PostVote(ModelBase):
    __tablename__ = "post_votes"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), primary_key=True)
    vote = db.Column(db.Integer, nullable=False)  # 1 = upvote, -1 = downvote

    user = db.relationship("Users", back_populates="post_votes")
    post = db.relationship("Posts", back_populates="post_votes")


class Posts(ModelBase):
    __tablename__ = 'posts'

    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    published = db.Column(db.Boolean, default=False) # Draft or publish
    is_public = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum(PostStatus), nullable=False, default=PostStatus.PENDING)

    comments = db.relationship("Comment", back_populates="post")
    user = db.relationship("Users", back_populates="posts")
    post_votes = db.relationship("PostVote", back_populates="post")

    search_vector = db.Column(TSVECTOR)

    def to_dict(self):
        data = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "published": self.published,
            "is_public": self.is_public,
            "status": self.status,
            "user_id": self.user_id,
        }
        return data


Index('posts_search_idx', Posts.search_vector, postgresql_using='gin')


@event.listens_for(Posts, 'before_insert')
@event.listens_for(Posts, 'before_update')
def update_search_vector(mapper, connection, target):
    content = ' '.join(filter(None, [target.title, target.content, target.summary]))
    target.search_vector = func.to_tsvector('simple', func.unaccent(content))

# CREATE EXTENSION IF NOT EXISTS unaccent;


class Comment(ModelBase):
    content = db.Column(db.String(300), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    post = db.relationship("Posts", back_populates="comments")
    user = db.relationship("Users", back_populates="comments")
