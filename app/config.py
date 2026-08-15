import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me-in-production")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Uploaded custom banners
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB
    ALLOWED_BANNER_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    BANNER_TARGET_SIZE = (1920, 1080)  # canvas size every banner is fit to


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
