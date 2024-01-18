import logging
import logging.config

import falcon

from api.config.config import get_logging_conf
from api.middleware.auth import AuthMiddleware
from api.repository.unit_of_work import AbstractUnitOfWork, SQLAlchemyUnitOfWork
from api.resources.exercises import ExercisesResource
from api.resources.food import FoodResource
from api.resources.humor import HumorResource
from api.resources.login import LoginResource
from api.resources.mood import MoodResource
from api.resources.sleep import SleepResource
from api.resources.water import WaterResource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")

uow = SQLAlchemyUnitOfWork()


def load_routes(app: falcon.App, uow: AbstractUnitOfWork) -> None:
    simpleLogger.info("Starting loading routes.")
    with uow:
        app.add_route("/login", LoginResource(uow))
        app.add_route("/register", LoginResource(uow), suffix="register")

        app.add_route("/humor", HumorResource(uow), suffix="add")
        app.add_route("/humor/{humor_id}", HumorResource(uow))
        app.add_route("/humor/date/{humor_date}", HumorResource(uow), suffix="date")

        app.add_route("/water-intake", WaterResource(uow), suffix="add")
        app.add_route("/water-intake/{water_intake_id}", WaterResource(uow))
        app.add_route(
            "/water-intake/date/{water_intake_date}", WaterResource(uow), suffix="date"
        )

        app.add_route("/exercises", ExercisesResource(uow), suffix="add")
        app.add_route("/exercises/{exercises_id}", ExercisesResource(uow))
        app.add_route(
            "/exercises/date/{exercises_date}", ExercisesResource(uow), suffix="date"
        )

        app.add_route("/food", FoodResource(uow), suffix="add")
        app.add_route("/food/{food_id}", FoodResource(uow))
        app.add_route("/food/date/{food_date}", FoodResource(uow), suffix="date")

        app.add_route("/sleep", SleepResource(uow), suffix="add")
        app.add_route("/sleep/{sleep_id}", SleepResource(uow))
        app.add_route("/sleep/date/{sleep_date}", SleepResource(uow), suffix="date")

        app.add_route("/mood", MoodResource(uow))
        app.add_route("/mood/{mood_id}", MoodResource(uow))
        app.add_route("/mood/date/{mood_date}", MoodResource(uow), suffix="date")
    simpleLogger.info("Routes added.")


def run(uow: AbstractUnitOfWork) -> falcon.App:
    simpleLogger.info("Starting the application.")
    middlewares = [AuthMiddleware(uow)]
    app = falcon.App(middleware=middlewares)
    load_routes(app, uow)

    return app


app = application = run(uow=uow)
