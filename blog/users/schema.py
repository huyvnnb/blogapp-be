from typing import Optional

from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str
    display_name: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    username: str
    display_name: str


class UserCreate(BaseModel):
    username: str
    password: str
    hashed_password: str | None = None
    display_name: str

    # @field_validator("password")
    # def hash_password(cls, v, info):
    #     hashed = bcrypt.hashpw(v.encode('utf-8'), bcrypt.gensalt())
    #     info.data['hashed_password'] = hashed.decode('utf-8')
    #     return v


class UserResponse(BaseModel):
    id: int
    username: str
    hashed_password: str | None = None
    display_name: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class TokenRequest(BaseModel):
    token: str


class UserEffective(BaseModel):
    user_id: int
    username: str
    display_name: str
    total_posts: int


class Me(BaseModel):
    user_id: int
    username: str
    display_name: Optional[str]


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    token: str


class UserPublicResponse(BaseModel):
    id: int
    username: str
    display_name: str

    @classmethod
    def from_entity(cls, user: "Users"):
        if user is None:
            return None
        return cls(
            id=user.id,
            username=user.username,
            display_name=user.display_name
        )


class UserPrivateResponse(BaseModel):
    id: int
    username: str
    display_name: str

    @classmethod
    def from_entity(cls, user: "Users"):
        if user is None:
            return None
        return cls(
            id=user.id,
            username=user.username,
            display_name=user.display_name
        )
