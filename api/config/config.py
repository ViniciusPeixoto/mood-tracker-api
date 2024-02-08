import os

from dynaconf import Dynaconf

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
    dbms = {
        "postgres": "postgresql",
        "mysql-connector": "mysql+mysqlconnector",
        "mysql-client": "mysql+mysqldb",
        "pymysql": "mysql+pymysql",
        "maria-connector": "mariadb+mariadbconnector",
    }
    db_dbms = settings.get("DB_DBMS")
    db_name = settings.get("DB_NAME")
    db_user = settings.get("DB_USER")
    db_password = settings.get("DB_PASSWORD")
    db_host = settings.get("DB_HOST")
    db_port = settings.get("DB_PORT")
    return f"{dbms[db_dbms]}://{db_user}:{db_password}@{db_host}{':'+db_port if db_port else ''}/{db_name}"


def get_logging_conf() -> str:
    return current_directory + "/" + settings.LOGGING_CONFIG


def get_jwt_secret_key() -> str:
    return settings.JWT_SECRET_KEY


def get_auth_ttl() -> int:
    return settings.AUTHENTICATION_TTL
