from blog import db
from blog.base.model import ModelBase

# from blog.utils.helper import get_password_hash, verify_password

role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)


user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class Permission(ModelBase):
    __tablename__ = 'permissions'

    name = db.Column(db.String(50), unique=True, nullable=False)

    roles = db.relationship("Role", secondary=role_permissions, back_populates="permissions")


class Role(ModelBase):
    __tablename__ = 'roles'

    name = db.Column(db.String(30), unique=True, nullable=False)
    permissions = db.relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = db.relationship("Users", secondary=user_roles, back_populates="roles")


class Users(ModelBase):
    __tablename__ = "users"

    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(30), nullable=True)

    posts = db.relationship("Posts", back_populates="user")
    roles = db.relationship('Role', secondary=user_roles, back_populates="users")
    comments = db.relationship("Comment", back_populates="user")
    post_votes = db.relationship("PostVote", back_populates="user")

    def set_password(self, password):
        from blog.utils.helper import get_password_hash
        self.hashed_password = get_password_hash(password)

    def check_password(self, password):
        from blog.utils.helper import verify_password
        return verify_password(password, self.hashed_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
        }


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'

    jti = db.Column(db.String(255), primary_key=True, unique=True)
    revoked_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
