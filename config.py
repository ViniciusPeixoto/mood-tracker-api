from dynaconf import Dynaconf

settings = Dynaconf(
    environments=True,
    load_dotenv=True,
    settings_files=["settings.toml", ".secrets.toml"],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
