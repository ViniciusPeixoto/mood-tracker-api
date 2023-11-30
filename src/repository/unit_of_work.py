from abc import ABC, abstractmethod
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import get_db_uri
from src.repository.models import Base
from src.repository.database import AbstractRepository, SQLRepository

engine = create_engine(get_db_uri(), echo=True)
# TODO: remove create tables from application 
Base.metadata.create_all(bind=engine)
DEFAULT_SESSION_FACTORY = sessionmaker(bind=engine, expire_on_commit=False)


class AbstractUnitOfWork(ABC):
    repository: AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.rollback()

    def commit(self):
        self._commit()

    def rollback(self):
        self._rollback()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def _rollback(self):
        raise NotImplementedError


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self, session_factory: Callable[[], Session] = DEFAULT_SESSION_FACTORY
    ) -> None:
        self.session_factory = session_factory

    def __enter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory()
        self.repository = SQLRepository(self.session)
        return super().__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def _rollback(self):
        self.session.rollback()
