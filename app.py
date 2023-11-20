import falcon

from src.repository.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from src.resources.humor import HumorResource
from src.resources.water import WaterResource
from src.resources.exercises import ExercisesResource
from src.resources.food import FoodResource
from src.resources.mood import MoodResource


def load_routes(app: falcon.App, uow: AbstractUnitOfWork):
    with uow:
        app.add_route("/humor", HumorResource(uow), suffix="add")
        app.add_route("/humor/{humor_id}", HumorResource(uow))
        app.add_route("/humor/date/{humor_date}", HumorResource(uow), suffix="date")

        app.add_route("/water-intake", WaterResource(uow), suffix="add")
        app.add_route("/water-intake/{water_intake_id}", WaterResource(uow))
        app.add_route("/water-intake/date/{water_intake_date}", WaterResource(uow), suffix="date")

        app.add_route("/exercises", ExercisesResource(uow), suffix="add")
        app.add_route("/exercises/{exercises_id}", ExercisesResource(uow))
        app.add_route("/exercises/date/{exercises_date}", ExercisesResource(uow), suffix="date")

        app.add_route("/food", FoodResource(uow), suffix="add")
        app.add_route("/food/{food_id}", FoodResource(uow))
        app.add_route("/food/date/{food_date}", FoodResource(uow), suffix="date")

        app.add_route("/mood", MoodResource(uow))
        app.add_route("/mood/{mood_id}", MoodResource(uow))
        app.add_route("/mood/date/{mood_date}", MoodResource(uow), suffix="date")


def run():
    uow = SQLAlchemyUnitOfWork()
    app = falcon.App()
    load_routes(app, uow)

    return app


app = application = run()
