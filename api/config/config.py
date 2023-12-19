import os

from dynaconf import Dynaconf

AUTHENTICATION_TTL = 5

current_directory = os.path.dirname(os.path.realpath(__file__))

settings = Dynaconf(
    root_path=current_directory,
    environments=True,
    load_dotenv=True,
    settings_files=["settings.toml", ".secrets.toml"],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.


def get_db_uri() -> str:
    db_name = settings.DB_NAME
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_host = settings.DB_HOST
    db_port = settings.DB_PORT
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_logging_conf() -> str:
    return current_directory + "/" + settings.LOGGING_CONFIG


def get_jwt_secret_key() -> str:
    return settings.JWT_SECRET_KEY
