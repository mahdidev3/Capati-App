from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600
    DATABASE_URL: str
    OTP_LENGTH : int = 6
    KAVENEGAR_API_KEY: str | None = None
    SENDER_NUMBER: str = "20006535"
    SIGNUP_OPT_TIME: int | None = 2
    LOGIN_OPT_TIME: int | None = 2
    CHANGE_MOBILE_OPT_TIME: int | None = 2
    SESSIONS_DIR: str | None = "./upload_sessions"
    WS_LOG_DIR: str | None = "./ws_connections"
    UPLOAD_DIR: str | None = "./uploads"
    URL_STORAGE_DIR : str | None = "./urls"
    TRANSLATED_DIR: str | None = "translated"
    ENVIRONMENT: str = "development"
    ADMIN_PHONE: str = "09923651580"
    MOBILE_PATTERN: str = "^09[0-9]{9}$"
    RECENT_PROJECTS_HOURS: int = 48
    UPLOAD_TOKEN_EXPIRE_HOURS: int = 2
    DOWNLOAD_TOKEN_EXPIRE_MINUTES: int = 30
    ESTIMATED_TRANSLATION_TIME: str = "30 دقیقه"
    ESTIMATED_TIME_REMAINING: str = "10 دقیقه"
    CHUNK_SIZE: int = 1024 * 1024
    MINIMUM_PAYMENT_AMOUNT: int = 5000
    BASE_URL : str = "http://127.0.0.1:8000"
    class Config:
        env_file = ".env"

settings = Settings()