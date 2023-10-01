import falcon

from src.repository.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from src.resources.humor import HumorResource
from src.resources.water import WaterResource


def load_routes(app: falcon.App, uow: AbstractUnitOfWork):
    with uow:
        app.add_route("/humor/{humor_id}", HumorResource(uow))
        app.add_route("/humor/date/{humor_date}", HumorResource(uow), suffix="date")
        app.add_route("/humor/", HumorResource(uow), suffix="add")

        app.add_route("/water-intake/{water_intake_id}", WaterResource(uow))
        app.add_route("/water-intake/date/{water_intake_date}", WaterResource(uow), suffix="date")
        app.add_route("/water-intake/", WaterResource(uow), suffix="add")


def run():
    uow = SQLAlchemyUnitOfWork()
    app = falcon.App()
    load_routes(app, uow)

    return app


app = application = run()
