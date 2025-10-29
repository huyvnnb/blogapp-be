import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY: str = os.environ.get("SECRET_KEY")

    DB_SERVER = os.getenv("DB_SERVER", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", False)

    ACCESS_EXPIRE_MINUTES = os.getenv("ACCESS_EXPIRE_MINUTES", 30)
    ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")

    REFRESH_EXPIRE_DAYS = os.getenv("REFRESH_EXPIRE_DAYS", 20)
    REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True


class TestConfig(Config):
    ENV = "test"
    TESTING = True

    DB_SERVER = os.getenv("DB_SERVER_TEST", "localhost")
    DB_PORT = os.getenv("DB_PORT_TEST", "5432")
    DB_NAME = os.getenv("DB_NAME_TEST", "blog_test")
    DB_USER = os.getenv("DB_USER_TEST", "test")
    DB_PASSWORD = os.getenv("DB_PASSWORD_TEST", "password")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
    )
