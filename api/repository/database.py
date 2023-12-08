from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.orm import Session, Query

from api.repository.models import Exercises, Food, Humor, Mood, Water


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
        return self.session.query(Mood).filter_by(id=mood_id).first()

    def _get_mood_by_date(self, mood_date: datetime) -> Query[Mood]:
        return self.session.query(Mood).filter_by(date=mood_date)

    def _delete_mood(self, mood: Mood) -> None:
        self.session.delete(mood)
