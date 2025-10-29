import uuid
from datetime import timedelta, datetime, timezone
from functools import wraps
from typing import Optional

import jwt
from flask import current_app, request

import bcrypt

from blog import ApiError, db
from blog.exception import NotFound, Unauthorized, Forbidden
from blog.users.schema import UserResponse, Me


def get_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str):
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _create_token(
        data: dict,
        expires_delta: timedelta,
        secret_key: str
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")

    return encoded_jwt


def create_access_token(data: dict):
    jti = str(uuid.uuid4())
    data = {**data, "jti": jti}
    encoded_jwt = _create_token(
        data,
        expires_delta=timedelta(minutes=int(current_app.config['ACCESS_EXPIRE_MINUTES'])),
        secret_key=current_app.config['ACCESS_SECRET_KEY']
    )

    return encoded_jwt


def create_refresh_token(data: dict):
    encoded_jwt = _create_token(
        data,
        expires_delta=timedelta(days=int(current_app.config['REFRESH_EXPIRE_DAYS'])),
        secret_key=current_app.config['REFRESH_SECRET_KEY']
    )

    return encoded_jwt


def _verify_token(token: str, secret_key: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms="HS256")
        if payload['user_id']:
            return payload['user_id']

        raise ApiError(message="Invalid token payload", status_code=401)

    except jwt.ExpiredSignatureError:
        raise ApiError(message="Token expired", status_code=401)
    except jwt.InvalidTokenError as e:
        raise ApiError(message=str(e), status_code=401)
    except Exception as e:
        raise e


def verify_access_token(token: str):
    return _verify_token(token, secret_key=current_app.config['ACCESS_SECRET_KEY'])


def verify_refresh_token(token: str):
    return _verify_token(token, secret_key=current_app.config['REFRESH_SECRET_KEY'])


# def verify_access_token(token: str):
#     try:
#         payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
#         print(f"Payload: {payload}")
#         if payload['user_id']:
#             return payload['user_id']
#     except jwt.ExpiredSignatureError:
#         raise ApiError(message="Token expired", status_code=401)
#     except jwt.InvalidTokenError as e:
#         raise ApiError(message=str(e))
#     except Exception as e:
#         raise e


def get_current_user():
    auth_header = request.headers.get("Authorization", None)

    if not auth_header:
        return None

    try:
        parts = auth_header.split(" ")
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return None

        token = parts[1]
        user_id = verify_access_token(token)
        if not user_id:
            raise Unauthorized("Invalid token")

        from blog.users import Users
        user = Users.query.filter(Users.id == user_id).first()
        if not user:
            raise NotFound("User not found")

        return user
    except jwt.ExpiredSignatureError as e:
        raise e

    except jwt.InvalidTokenError as e:
        raise e


def get_jwt_token():
    auth_header = request.headers.get("Authorization", None)

    if not auth_header:
        return None

    try:
        parts = auth_header.split(" ")
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return None

        token = parts[1]
        return token

    except jwt.ExpiredSignatureError as e:
        raise e

    except jwt.InvalidTokenError as e:
        raise e


def extract_payload(token: str):
    try:
        payload = jwt.decode(token, current_app.config['ACCESS_SECRET_KEY'], algorithms="HS256")
        if payload and payload['jti'] and payload['user_id']:
            return payload

        raise ApiError(message="Invalid token payload", status_code=401)

    except jwt.ExpiredSignatureError:
        raise ApiError(message="Token expired", status_code=401)
    except jwt.InvalidTokenError as e:
        raise ApiError(message=str(e), status_code=401)
    except Exception as e:
        raise e


def get_token_jti(token: str):
    payload = extract_payload(token)
    if payload['jti']:
        return payload['jti']


def token_require(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            raise Unauthorized("Please login first")

        try:
            parts = auth_header.split(" ")
            if parts[0].lower() != 'bearer' or len(parts) != 2:
                raise Unauthorized("Invalid token")

            token = parts[1]
            user_id = verify_access_token(token)
            if not user_id:
                raise Unauthorized("Invalid token")

            from blog.users import Users
            user = Users.query.filter(Users.id == user_id).first()
            if not user:
                raise NotFound("User not found")

            return f(
                user=Me(user_id=user.id, username=user.username, display_name=user.display_name),
                *args, **kwargs
            )
        except jwt.ExpiredSignatureError as e:
            raise e

        except jwt.InvalidTokenError as e:
            raise e

    return wrapper


def is_token_revoked(jti: str) -> bool:
    from blog.users import RevokedToken
    return RevokedToken.query.filter_by(jti=jti).first() is not None


def token_require_with_check_revoked(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            raise Unauthorized("Please login first")

        try:
            parts = auth_header.split(" ")
            if parts[0].lower() != 'bearer' or len(parts) != 2:
                raise Unauthorized("Invalid token")

            token = parts[1]
            payload = extract_payload(token)
            user_id = payload['user_id']
            if not user_id:
                raise Unauthorized("Invalid token")

            jti = get_token_jti(token)
            print(f"JTI: {jti}")
            if is_token_revoked(jti):
                raise Unauthorized("Token has been revoked")

            from blog.users import Users
            user = Users.query.filter(Users.id == user_id).first()
            if not user:
                raise NotFound("User not found")

            return f(
                user=Me(user_id=user.id, username=user.username, display_name=user.display_name),
                *args, **kwargs
            )
        except jwt.ExpiredSignatureError as e:
            raise Unauthorized("Token has expired")

        except jwt.InvalidTokenError as e:
            raise Unauthorized("Invalid token")

    return wrapper


def role_require(*required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(f"Check role: {required_role}")
            user = kwargs.get("user")

            from blog.users import Users, user_roles, Role
            roles = (db.session.query(Role.name)
                     .join(user_roles, Role.id == user_roles.c.role_id)
                     .filter(user_roles.c.user_id == user.user_id)
                     .all())
            available_roles = [r[0] for r in roles]
            for role in required_role:
                if role not in available_roles:
                    raise Forbidden("You do not have privilege to do this action.")

            return f(*args, **kwargs)

        return wrapper

    return decorator


# def require_permission(*require_permission):
#     def decorator(f):
#         @wraps
#         def wrapper(*args, **kwargs):
#             user = kwargs.get("user")

