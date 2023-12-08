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

    mood: Mapped["Mood"] = relationship(
        back_populates="humor", cascade="all, delete-orphan"
    )

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

    mood: Mapped["Mood"] = relationship(
        back_populates="water_intake", cascade="all, delete-orphan"
    )

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

    mood: Mapped["Mood"] = relationship(
        back_populates="exercises", cascade="all, delete-orphan"
    )

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

    mood: Mapped["Mood"] = relationship(
        back_populates="food_habits", cascade="all, delete-orphan"
    )

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
    humor_id: Mapped[int] = mapped_column(ForeignKey("user_humor.id"))
    water_intake_id: Mapped[int] = mapped_column(ForeignKey("user_water_intake.id"))
    exercises_id: Mapped[int] = mapped_column(ForeignKey("user_exercises.id"))
    food_habits_id: Mapped[int] = mapped_column(ForeignKey("user_food_habits.id"))

    humor: Mapped["Humor"] = relationship(back_populates="mood")
    water_intake: Mapped["Water"] = relationship(back_populates="mood")
    exercises: Mapped["Exercises"] = relationship(back_populates="mood")
    food_habits: Mapped["Food"] = relationship(back_populates="mood")

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
