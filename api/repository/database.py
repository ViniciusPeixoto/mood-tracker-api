from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.orm import Query, Session, joinedload

from api.repository.models import Exercises, Food, Humor, Mood, User, UserAuth, Water


class AbstractRepository(ABC):
    def add_humor(self, humor: Humor) -> None:
        self._add_humor(humor)

    def get_humor_by_id(self, humor_id: int) -> Humor:
        return self._get_humor_by_id(humor_id)

    def get_humor_by_date(self, humor_date: datetime) -> Query[Humor]:
        return self._get_humor_by_date(humor_date)

    def update_humor(self, humor: Humor, humor_data: dict) -> None:
        self._update_humor(humor, humor_data)

    def delete_humor(self, humor: Humor) -> None:
        self._delete_humor(humor)

    def add_water_intake(self, water_intake: Water) -> None:
        self._add_water_intake(water_intake)

    def get_water_intake_by_id(self, water_intake_id: int) -> Water:
        return self._get_water_intake_by_id(water_intake_id)

    def get_water_intake_by_date(self, water_intake_date: datetime) -> Query[Water]:
        return self._get_water_intake_by_date(water_intake_date)

    def update_water_intake(self, water_intake: Water, water_intake_data: dict) -> None:
        self._update_water_intake(water_intake, water_intake_data)

    def delete_water_intake(self, water_intake: Water) -> None:
        self._delete_water_intake(water_intake)

    def add_exercises(self, exercises: Exercises) -> None:
        self._add_exercises(exercises)

    def get_exercises_by_id(self, exercises_id: int) -> Exercises:
        return self._get_exercises_by_id(exercises_id)

    def get_exercises_by_date(self, exercises_date: datetime) -> Query[Exercises]:
        return self._get_exercises_by_date(exercises_date)

    def update_exercises(self, exercises: Exercises, exercises_data: dict) -> None:
        self._update_exercises(exercises, exercises_data)

    def delete_exercises(self, exercises: Exercises) -> None:
        self._delete_exercises(exercises)

    def add_food_habits(self, food_habits: Food) -> None:
        self._add_food_habits(food_habits)

    def get_food_habits_by_id(self, food_habits_id: int) -> Food:
        return self._get_food_habits_by_id(food_habits_id)

    def get_food_habits_by_date(self, food_habits_date: datetime) -> Query[Food]:
        return self._get_food_habits_by_date(food_habits_date)

    def update_food_habits(self, food_habits: Food, food_habits_data: dict) -> None:
        self._update_food_habits(food_habits, food_habits_data)

    def delete_food_habits(self, food_habits: Food) -> None:
        self._delete_food_habits(food_habits)

    def add_mood(self, mood: Mood) -> None:
        self._add_mood(mood)

    def get_mood_by_id(self, mood_id: int) -> Mood:
        return self._get_mood_by_id(mood_id)

    def get_mood_by_date(self, mood_date: datetime) -> Query[Mood]:
        return self._get_mood_by_date(mood_date)

    def delete_mood(self, mood: Mood) -> None:
        self._delete_mood(mood)

    def add_user(self, user: User) -> None:
        self._add_user(user)

    def get_user_by_id(self, user_id: int) -> User:
        return self._get_user_by_id(user_id)

    def update_user(self, user: User, user_data: dict) -> None:
        self._update_user(user, user_data)

    def add_user_auth(self, user_auth: UserAuth) -> None:
        self._add_user_auth(user_auth)

    def get_all_user_auth(self) -> Query[UserAuth]:
        return self._get_all_user_auth()

    def get_user_auth_by_username(self, username: str) -> UserAuth:
        return self._get_user_auth_by_username(username)

    def update_user_auth(self, user_auth: UserAuth, user_auth_data: dict) -> None:
        self._update_user_auth(user_auth, user_auth_data)

    def deactivate_user_auth(self, user_auth: UserAuth) -> None:
        self._deactivate_user_auth(user_auth)

    def delete_user_auth(self, user_auth: UserAuth) -> None:
        self._delete_user_auth(user_auth)

    @abstractmethod
    def _add_humor(self, humor: Humor) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_humor_by_id(self, humor_id: int) -> Humor:
        raise NotImplementedError

    @abstractmethod
    def _get_humor_by_date(self, humor_date: datetime) -> Query[Humor]:
        raise NotImplementedError

    @abstractmethod
    def _update_humor(self, humor: Humor, humor_data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def _delete_humor(self, humor: Humor) -> Humor:
        raise NotImplementedError

    @abstractmethod
    def _add_water_intake(self, water_intake: Water) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_water_intake_by_id(self, water_intake_id: int) -> Water:
        raise NotImplementedError

    @abstractmethod
    def _get_water_intake_by_date(self, water_intake_date: datetime) -> Query[Water]:
        raise NotImplementedError

    @abstractmethod
    def _update_water_intake(
        self, water_intake: Water, water_intake_data: dict
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def _delete_water_intake(self, water_intake: Water) -> None:
        raise NotImplementedError

    @abstractmethod
    def _add_exercises(self, exercises: Exercises) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_exercises_by_id(self, exercises_id: int) -> Exercises:
        raise NotImplementedError

    @abstractmethod
    def _get_exercises_by_date(self, exercises_date: datetime) -> Query[Exercises]:
        raise NotImplementedError

    @abstractmethod
    def _update_exercises(self, exercises: Exercises, exercises_data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def _delete_exercises(self, exercises: Exercises) -> None:
        raise NotImplementedError

    @abstractmethod
    def _add_food_habits(self, food_habits: Food) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_food_habits_by_id(self, food_habits_id: int) -> Food:
        raise NotImplementedError

    @abstractmethod
    def _get_food_habits_by_date(self, food_habits_date: datetime) -> Query[Food]:
        raise NotImplementedError

    @abstractmethod
    def _update_food_habits(self, food_habits: Food, food_habits_data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def _delete_food_habits(self, food_habits: Food) -> None:
        raise NotImplementedError

    @abstractmethod
    def _add_mood(self, mood: Mood) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_mood_by_id(self, mood_id: int) -> Mood:
        raise NotImplementedError

    @abstractmethod
    def _get_mood_by_date(self, mood_date: datetime) -> Query[Mood]:
        raise NotImplementedError

    @abstractmethod
    def _delete_mood(self, mood: Mood) -> None:
        raise NotImplementedError

    @abstractmethod
    def _add_user(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_user_by_id(self, user_id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    def _update_user(self, user: User, user_data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def _add_user_auth(self, user_auth: UserAuth) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_all_user_auth(self) -> Query[UserAuth]:
        raise NotImplementedError

    @abstractmethod
    def _get_user_auth_by_username(self, username: str) -> UserAuth:
        raise NotImplementedError

    @abstractmethod
    def _update_user_auth(self, user_auth: UserAuth, user_auth_data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def _deactivate_user_auth(self, user_auth: UserAuth) -> None:
        raise NotImplementedError

    @abstractmethod
    def _delete_user_auth(self, user_auth: UserAuth) -> None:
        raise NotImplementedError


class SQLRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def _add_humor(self, humor: Humor) -> None:
        self.session.add(humor)

    def _get_humor_by_id(self, humor_id: int) -> Humor:
        return self.session.query(Humor).filter_by(id=humor_id).first()

    def _get_humor_by_date(self, humor_date: datetime) -> Query[Humor]:
        return self.session.query(Humor).filter_by(date=humor_date)

    def _update_humor(self, humor: Humor, humor_data: dict) -> None:
        for key in humor_data:
            setattr(humor, key, humor_data[key])

    def _delete_humor(self, humor: Humor) -> None:
        self.session.delete(humor)

    def _add_water_intake(self, water_intake: Water) -> None:
        self.session.add(water_intake)

    def _get_water_intake_by_id(self, water_intake_id: int) -> Water:
        return self.session.query(Water).filter_by(id=water_intake_id).first()

    def _get_water_intake_by_date(self, water_intake_date: datetime) -> Query[Water]:
        return self.session.query(Water).filter_by(date=water_intake_date)

    def _update_water_intake(
        self, water_intake: Water, water_intake_data: dict
    ) -> None:
        for key in water_intake_data:
            setattr(water_intake, key, water_intake_data[key])

    def _delete_water_intake(self, water_intake: Water) -> None:
        self.session.delete(water_intake)

    def _add_exercises(self, exercises: Exercises) -> None:
        self.session.add(exercises)

    def _get_exercises_by_id(self, exercises_id: int) -> Exercises:
        return self.session.query(Exercises).filter_by(id=exercises_id).first()

    def _get_exercises_by_date(self, exercises_date: datetime) -> Query[Exercises]:
        return self.session.query(Exercises).filter_by(date=exercises_date)

    def _update_exercises(self, exercises: Exercises, exercises_data: dict) -> None:
        for key in exercises_data:
            setattr(exercises, key, exercises_data[key])

    def _delete_exercises(self, exercises: Exercises) -> None:
        self.session.delete(exercises)

    def _add_food_habits(self, food_habits: Food) -> None:
        self.session.add(food_habits)

    def _get_food_habits_by_id(self, food_habits_id: int) -> Food:
        return self.session.query(Food).filter_by(id=food_habits_id).first()

    def _get_food_habits_by_date(self, food_habits_date: datetime) -> Query[Food]:
        return self.session.query(Food).filter_by(date=food_habits_date)

    def _update_food_habits(self, food_habits: Food, food_habits_data: dict) -> None:
        for key in food_habits_data:
            setattr(food_habits, key, food_habits_data[key])

    def _delete_food_habits(self, food_habits: Food) -> None:
        self.session.delete(food_habits)

    def _add_mood(self, mood: Mood) -> None:
        self.session.add(mood)

    def _get_mood_by_id(self, mood_id: int) -> Mood:
        mood = (
            self.session.query(Mood)
            .options(
                joinedload(Mood.exercises),
                joinedload(Mood.food_habits),
                joinedload(Mood.humors),
                joinedload(Mood.water_intakes),
            )
            .filter_by(id=mood_id)
            .first()
        )
        return mood

    def _get_mood_by_date(self, mood_date: datetime) -> Query[Mood]:
        moods_query = (
            self.session.query(Mood)
            .options(
                joinedload(Mood.exercises),
                joinedload(Mood.food_habits),
                joinedload(Mood.humors),
                joinedload(Mood.water_intakes),
            )
            .filter_by(date=mood_date)
        )
        return moods_query

    def _delete_mood(self, mood: Mood) -> None:
        self.session.delete(mood)

    def _add_user(self, user: User) -> None:
        self.session.add(user)

    def _get_user_by_id(self, user_id: int) -> User:
        return self.session.query(User).filter_by(id=user_id).first()

    def _update_user(self, user: User, user_data: dict) -> None:
        for key in user_data:
            setattr(user, key, user_data[key])

    def _add_user_auth(self, user_auth: UserAuth) -> None:
        self.session.add(user_auth)

    def _get_all_user_auth(self) -> Query[UserAuth]:
        return self.session.query(UserAuth)

    def _get_user_auth_by_username(self, username: str) -> UserAuth:
        return self.session.query(UserAuth).filter_by(username=username).first()

    def _update_user_auth(self, user_auth: UserAuth, user_auth_data: dict) -> None:
        for key in user_auth_data:
            setattr(user_auth, key, user_auth_data[key])

    def _deactivate_user_auth(self, user_auth: UserAuth) -> None:
        setattr(user_auth, "active", False)

    def _delete_user_auth(self, user_auth: UserAuth) -> None:
        self.session.delete(user_auth)
