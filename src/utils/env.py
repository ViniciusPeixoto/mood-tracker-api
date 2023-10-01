from config import settings


def get_db_uri() -> str:
    db_name = settings.DB_NAME
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_host = settings.DB_HOST
    db_port = settings.DB_PORT
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
