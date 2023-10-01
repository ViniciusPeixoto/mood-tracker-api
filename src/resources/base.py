from src.repository.unit_of_work import AbstractUnitOfWork


class Resource:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow
