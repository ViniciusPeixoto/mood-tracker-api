import logging
import logging.config

from api.config.config import get_logging_conf
from api.repository.models import User, Mood
from api.repository.unit_of_work import AbstractUnitOfWork


logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class Resource:
    """
    Base class for Resources. It has everything that is common to all resources.
    """

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def _get_user(self, username: str) -> User:
        if not username:
            return None

        user_id = self.uow.repository.get_user_auth_by_username(username).user_id
        if not user_id:
            return None

        return self.uow.repository.get_user_by_id(user_id)


    def _get_mood_from_date(self, date: str, user_id: int) -> Mood:
        mood = self.uow.repository.get_mood_by_date(date).filter_by(user_id=user_id).first()
        if mood:
            return mood

        mood = Mood(user_id=user_id, date=date)
        try:
            self.uow.repository.add_mood(mood)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add mood operation!", exc_info=True
            )
            return
        return self.uow.repository.get_mood_by_date(date).filter_by(user_id=user_id).first()
