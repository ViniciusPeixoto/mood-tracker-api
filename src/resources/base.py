from src.repository.unit_of_work import AbstractUnitOfWork


class Resource:
    """
    Base class for Resources. It has everything that is common to all resources.
    """
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow
