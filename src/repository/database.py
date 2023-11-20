from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.orm import Session

from src.repository.models import Exercises, Food, Humor, Mood, Water


class AbstractRepository(ABC):
    def add_humor(self, humor: Humor) -> None:
        self._add_humor(humor)

    def get_humor_by_id(self, humor_id: int):
        return self._get_humor_by_id(humor_id)

    def get_humor_by_date(self, humor_date: datetime):
        return self._get_humor_by_date(humor_date)

    def add_water_intake(self, water_intake: Water):
        self._add_water_intake(water_intake)

    def get_water_intake_by_id(self, water_intake_id: int):
        return self._get_water_intake_by_id(water_intake_id)

    def get_water_intake_by_date(self, water_intake_date: datetime):
        return self._get_water_intake_by_date(water_intake_date)

    def add_exercises(self, exercises: Exercises):
        self._add_exercises(exercises)

    def get_exercises_by_id(self, exercises_id: int):
        return self._get_exercises_by_id(exercises_id)

    def get_exercises_by_date(self, exercises_date: datetime):
        return self._get_exercises_by_date(exercises_date)

    def add_food_habits(self, food_habits: Food):
        self._add_food_habits(food_habits)

    def get_food_habits_by_id(self, food_habits_id: int):
        return self._get_food_habits_by_id(food_habits_id)

    def get_food_habits_by_date(self, food_habits_date: datetime):
        return self._get_food_habits_by_date(food_habits_date)

    def add_mood(self, mood: Mood):
        self._add_mood(mood)

    def get_mood_by_id(self, mood_id: int):
        return self._get_mood_by_id(mood_id)

    def get_mood_by_date(self, mood_date: datetime):
        return self._get_mood_by_date(mood_date)

    @abstractmethod
    def _add_humor(self, humor: Humor) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_humor_by_id(self, humor_id: int) -> Humor:
        raise NotImplementedError

    @abstractmethod
    def _get_humor_by_date(self, humor_date: datetime) -> Humor:
        raise NotImplementedError

    @abstractmethod
    def _add_water_intake(self, water_intake: Water) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_water_intake_by_id(self, water_intake_id: int) -> Water:
        raise NotImplementedError

    @abstractmethod
    def _get_water_intake_by_date(self, water_intake_date: datetime) -> Water:
        raise NotImplementedError

    @abstractmethod
    def _add_exercises(self, exercises: Exercises) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_exercises_by_id(self, exercises_id: int) -> Exercises:
        raise NotImplementedError

    @abstractmethod
    def _get_exercises_by_date(self, exercises_date: datetime) -> Exercises:
        raise NotImplementedError

    @abstractmethod
    def _add_food_habits(self, food_habits: Food) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_food_habits_by_id(self, food_habits_id: int) -> Food:
        raise NotImplementedError

    @abstractmethod
    def _get_food_habits_by_date(self, food_habits_date: datetime) -> Food:
        raise NotImplementedError

    @abstractmethod
    def _add_mood(self, mood: Mood) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_mood_by_id(self, mood_id: int) -> Mood:
        raise NotImplementedError

    @abstractmethod
    def _get_mood_by_date(self, mood_date: datetime) -> Mood:
        raise NotImplementedError


class SQLRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def _add_humor(self, humor: Humor) -> None:
        self.session.add(humor)

    def _get_humor_by_id(self, humor_id: int) -> Humor:
        return self.session.query(Humor).filter_by(id=humor_id).first()

    def _get_humor_by_date(self, humor_date: datetime) -> Humor:
        return self.session.query(Humor).filter_by(date=humor_date).first()

    def _add_water_intake(self, water_intake: Water) -> None:
        self.session.add(water_intake)

    def _get_water_intake_by_id(self, water_intake_id: int) -> Water:
        return self.session.query(Water).filter_by(id=water_intake_id).first()

    def _get_water_intake_by_date(self, water_intake_date: datetime) -> Water:
        return self.session.query(Water).filter_by(date=water_intake_date).first()

    def _add_exercises(self, exercises: Exercises) -> None:
        self.session.add(exercises)

    def _get_exercises_by_id(self, exercises_id: int) -> Exercises:
        return self.session.query(Exercises).filter_by(id=exercises_id).first()

    def _get_exercises_by_date(self, exercises_date: datetime) -> Exercises:
        return self.session.query(Exercises).filter_by(date=exercises_date).first()

    def _add_food_habits(self, food_habits: Food) -> None:
        self.session.add(food_habits)

    def _get_food_habits_by_id(self, food_habits_id: int) -> Food:
        return self.session.query(Food).filter_by(id=food_habits_id).first()

    def _get_food_habits_by_date(self, food_habits_date: datetime) -> Food:
        return self.session.query(Food).filter_by(date=food_habits_date).first()

    def _add_mood(self, mood: Mood) -> None:
        self.session.add(mood)

    def _get_mood_by_id(self, mood_id: int) -> Mood:
        return self.session.query(Mood).filter_by(id=mood_id).first()

    def _get_mood_by_date(self, mood_date: datetime) -> Mood:
        return self.session.query(Mood).filter_by(date=mood_date).first()
