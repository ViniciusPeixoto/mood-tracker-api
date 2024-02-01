import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Humor(Base):
    __tablename__ = "user_humor"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(Date, default=datetime.today().date())
    value: Mapped[int] = mapped_column(Integer, default=5)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    health_based: Mapped[bool] = mapped_column(Boolean, default=False)

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="humors")

    def __str__(self) -> str:
        return f'{{\
            "id":"{self.id}", \
            "date":"{self.date}", \
            "value":"{self.value}", \
            "description":"{self.description}", \
            "health_based":"{self.health_based}"\
        }}'

    def __repr__(self) -> str:
        return f'Humor("id"="{self.id}", "date"="{self.date}", "value"="{self.value}", "description"="{self.description}", "health_based"="{self.health_based}")'

    def __eq__(self, other: object) -> bool:
        return all(
            [
                str(self.date) == str(other.date),
                self.value == other.value,
                self.description == other.description,
                self.health_based == other.health_based,
            ]
        )

    def as_dict(self) -> dict:
        return {
            col.name: str(getattr(self, col.name)) for col in self.__table__.columns
        }


class Water(Base):
    __tablename__ = "user_water_intake"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(Date, default=datetime.today().date())
    milliliters: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    pee: Mapped[bool] = mapped_column(Boolean, default=False)

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="water_intakes")

    def __str__(self) -> str:
        return f'{{\
            "id":"{self.id}", \
            "date":"{self.date}", \
            "milliliters":"{self.milliliters}", \
            "description":"{self.description}", \
            "pee":"{self.pee}"\
        }}'

    def __repr__(self) -> str:
        return f'Water Intake("id"="{self.id}", "date"="{self.date}", "milliliters"="{self.milliliters}", "description"="{self.description}", "pee"="{self.pee}")'

    def __eq__(self, other: object) -> bool:
        return all(
            [
                str(self.date) == str(other.date),
                self.milliliters == other.milliliters,
                self.description == other.description,
                self.pee == other.pee,
            ]
        )

    def as_dict(self) -> dict:
        return {
            col.name: str(getattr(self, col.name)) for col in self.__table__.columns
        }


class Exercises(Base):
    __tablename__ = "user_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(Date, default=datetime.today().date())
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="exercises")

    def __str__(self) -> str:
        return f'{{"id":"{self.id}", "date":"{self.date}", "minutes":"{self.minutes}", "description":"{self.description}"}}'

    def __repr__(self) -> str:
        return f'Exercises("id"="{self.id}", "date"="{self.date}", "minutes"="{self.minutes}", "description"="{self.description}")'

    def __eq__(self, other: object) -> bool:
        return all(
            [
                str(self.date) == str(other.date),
                self.minutes == other.minutes,
                self.description == other.description,
            ]
        )

    def as_dict(self) -> dict:
        return {
            col.name: str(getattr(self, col.name)) for col in self.__table__.columns
        }


class Food(Base):
    __tablename__ = "user_food_habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(Date, default=datetime.today().date())
    value: Mapped[int] = mapped_column(Integer, default=5)
    description: Mapped[str] = mapped_column(String(256), nullable=True)

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="food_habits")

    def __str__(self) -> str:
        return f'{{\
            "id":"{self.id}", \
            "date":"{self.date}", \
            "value":"{self.value}", \
            "description":"{self.description}" \
        }}'

    def __repr__(self) -> str:
        return f'Food Habits("id"="{self.id}", "date"="{self.date}", "value"="{self.value}", "description"="{self.description}")'

    def __eq__(self, other: object) -> bool:
        return all(
            [
                str(self.date) == str(other.date),
                self.value == other.value,
                self.description == other.description,
            ]
        )

    def as_dict(self) -> dict:
        return {
            col.name: str(getattr(self, col.name)) for col in self.__table__.columns
        }


class Sleep(Base):
    __tablename__ = "user_sleep"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(Date, default=datetime.today().date())
    value: Mapped[int] = mapped_column(Integer, default=5)
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="sleeps")

    def __str__(self) -> str:
        return f'{{\
            "id":"{self.id}", \
            "date":"{self.date}", \
            "value":"{self.value}", \
            "minutes":"{self.minutes}"\
            "description":"{self.description}", \
        }}'

    def __repr__(self) -> str:
        return f'Sleep("id"="{self.id}", "date"="{self.date}", "value"="{self.value}", "minutes"="{self.minutes}", "description"="{self.description}")'

    def __eq__(self, other: object) -> bool:
        return all(
            [
                str(self.date) == str(other.date),
                self.value == other.value,
                self.minutes == other.minutes,
                self.description == other.description,
            ]
        )

    def as_dict(self) -> dict:
        return {
            col.name: str(getattr(self, col.name)) for col in self.__table__.columns
        }


class Mood(Base):
    __tablename__ = "user_mood"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(
        Date, default=datetime.today().date(), unique=True
    )
    score: Mapped[int] = mapped_column(Integer, default=0)

    humors: Mapped[List["Humor"]] = relationship(
        back_populates="mood", cascade="all, delete-orphan"
    )
    water_intakes: Mapped[List["Water"]] = relationship(
        back_populates="mood", cascade="all, delete-orphan"
    )
    exercises: Mapped[List["Exercises"]] = relationship(
        back_populates="mood", cascade="all, delete-orphan"
    )
    food_habits: Mapped[List["Food"]] = relationship(
        back_populates="mood", cascade="all, delete-orphan"
    )
    sleeps: Mapped[List["Sleep"]] = relationship(
        back_populates="mood", cascade="all, delete-orphan"
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="moods")

    def __str__(self) -> str:
        exercises = [str(exercises) for exercises in self.exercises]
        humors = [str(humor) for humor in self.humors]
        food_habits = [str(food_habits) for food_habits in self.food_habits]
        water_intakes = [str(water_intakes) for water_intakes in self.water_intakes]
        return f'{{\
            "id":"{self.id}", \
            "date":"{self.date}", \
            "score: {self.score}", \
            "humor":{humors}, \
            "water_intake":{water_intakes}, \
            "exercises":{exercises}, \
            "food_habits":{food_habits}\
        }}'

    def __repr__(self) -> str:
        return f'Mood("id"="{self.id}", "date"="{self.date}", "score"="{self.score}", "humor"={self.humors}, "water_intake"={self.water_intakes}, "exercises"={self.exercises}, "food_habits"={self.food_habits})'

    def __eq__(self, other: object) -> bool:
        return all(
            [
                str(self.date) == str(other.date),
                self.score == other.score,
                self.humors == other.humors,
                self.water_intakes == other.water_intakes,
                self.exercises == other.exercises,
                self.food_habits == other.food_habits,
            ]
        )

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d.pop("_sa_instance_state")
        for key in d:
            if key not in ["id", "user_id", "date", "score"]:
                d[key] = [item.as_dict() for item in d[key]]
            else:
                d[key] = str(d[key])
        return d


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    moods: Mapped[List["Mood"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    user_auth: Mapped["UserAuth"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return f'{{"id":"{self.id}"}}'

    def __repr__(self) -> str:
        return f'User("id"="{self.id}")'

    def as_dict(self) -> dict:
        return {
            col.name: str(getattr(self, col.name)) for col in self.__table__.columns
        }


class UserAuth(Base):
    __tablename__ = "user_auth"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True)
    password: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now())
    last_login: Mapped[datetime] = mapped_column(Date, default=datetime.now())
    token: Mapped[str] = mapped_column(String(512))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="user_auth")
