import os

from dotenv import load_dotenv

load_dotenv()


def env(varname: str, ignore_empty: bool = False) -> str:
    """
    try to load an env variable.
    Raise an exception if env does not exist.
    """

    val = os.getenv(varname)
    if not val and not ignore_empty:
        raise Exception(f"env {varname} not set!")
    return val or ""

DATABASE_URL = env("DATABASE_URL")
DATABASE_URL_SYNC = env("DATABASE_URL_SYNC")
# RESEND_API_KEY=env("RESEND_API_KEY")
GMAIL_SMTP_USERNAME = env("GMAIL_SMTP_USERNAME")
GMAIL_SMTP_SENDER = env("GMAIL_SMTP_SENDER")
GMAIL_SMTP_REFRESH_TOKEN = env("GMAIL_SMTP_REFRESH_TOKEN")
GMAIL_SMTP_CLIENTID = env("GMAIL_SMTP_CLIENTID")
GMAIL_SMTP_CLIENT_SECRET = env("GMAIL_SMTP_CLIENT_SECRET")

SECRET_KEY=env("SECRET_KEY")
ALGORITHM=env("ALGORITHM",ignore_empty=True) or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=int(env("ACCESS_TOKEN_EXPIRE_MINUTES",ignore_empty=True) or "1440")
