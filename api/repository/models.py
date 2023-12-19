from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Humor(Base):
    __tablename__ = "user_humor"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        Date, default=datetime.today().date()
    )
    value: Mapped[int] = mapped_column(Integer, default=5)
    description: Mapped[Optional[str]]
    health_based: Mapped[bool] = mapped_column(Boolean, default=False)

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="humor")

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


class Water(Base):
    __tablename__ = "user_water_intake"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        Date, default=datetime.today().date()
    )
    milliliters: Mapped[int]
    description: Mapped[Optional[str]]
    pee: Mapped[bool] = mapped_column(Boolean, default=False)

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="water_intake")

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


class Exercises(Base):
    __tablename__ = "user_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        Date, default=datetime.today().date()
    )
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]]

    mood_id: Mapped[int] = mapped_column(ForeignKey("user_mood.id"))
    mood: Mapped["Mood"] = relationship(back_populates="exercises")

    def __str__(self) -> str:
        return f'{{\
            "id":"{self.id}", \
            "date":"{self.date}", \
            "minutes":"{self.minutes}", \
            "description":"{self.description}" \
        }}'

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


class Food(Base):
    __tablename__ = "user_food_habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        Date, default=datetime.today().date()
    )
    value: Mapped[int]
    description: Mapped[str] = mapped_column(String(256))

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


class Mood(Base):
    __tablename__ = "user_mood"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        Date, default=datetime.today().date()
    )

    humor: Mapped["Humor"] = relationship(back_populates="mood", cascade="all, delete-orphan")
    water_intake: Mapped["Water"] = relationship(back_populates="mood", cascade="all, delete-orphan")
    exercises: Mapped["Exercises"] = relationship(back_populates="mood", cascade="all, delete-orphan")
    food_habits: Mapped["Food"] = relationship(back_populates="mood", cascade="all, delete-orphan")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="mood")

    def __str__(self) -> str:
        return f'{{\
            "id":"{self.id}", \
            "date":"{self.date}", \
            "humor":{self.humor}, \
            "water_intake":{self.water_intake}, \
            "exercises":{self.exercises}, \
            "food_habits":{self.food_habits}\
        }}'

    def __repr__(self) -> str:
        return f'Mood("id"="{self.id}", "date"="{self.date}", "humor"={self.humor}, "water_intake"={self.water_intake}, "exercises"={self.exercises}, "food_habits"={self.food_habits})'

    def __eq__(self, other: object) -> bool:
        return all(
            [
                str(self.date) == str(other.date),
                self.humor == other.humor,
                self.water_intake == other.water_intake,
                self.exercises == other.exercises,
                self.food_habits == other.food_habits,
            ]
        )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    mood: Mapped["Mood"] = relationship(back_populates="user", cascade="all, delete-orphan")
    user_auth: Mapped["UserAuth"] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f'{{"id":"{self.id}"}}'

    def __repr__(self) -> str:
        return f'User("id"="{self.id}")'


class UserAuth(Base):
    __tablename__ = "user_auth"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(128))
    password: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(
        Date, default=datetime.today().date()
    )
    last_login: Mapped[datetime] = mapped_column(
        Date, default=datetime.today().date()
    )
    token: Mapped[str] = mapped_column(String(512))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="user_auth")
