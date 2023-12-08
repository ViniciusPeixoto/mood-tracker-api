from abc import ABC, abstractmethod
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.config.config import get_db_uri
from api.repository.database import AbstractRepository, SQLRepository
from api.repository.models import Base

engine = create_engine(get_db_uri(), echo=True)
# TODO: remove create tables from application
Base.metadata.create_all(bind=engine)
DEFAULT_SESSION = sessionmaker(bind=engine, expire_on_commit=False)()


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

    def flush(self):
        self._flush()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def _rollback(self):
        raise NotImplementedError

    @abstractmethod
    def _flush(self):
        raise NotImplementedError


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: Callable[[], Session] = DEFAULT_SESSION) -> None:
        self.session = session

    def __enter__(self) -> AbstractUnitOfWork:
        self.repository = SQLRepository(self.session)
        return super().__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def _rollback(self):
        self.session.rollback()

    def _flush(self):
        self.session.flush()
