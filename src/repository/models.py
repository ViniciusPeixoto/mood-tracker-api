from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Humor(Base):
    __tablename__ = "user_humor"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.today().date())
    value: Mapped[int] = mapped_column(Integer, default=5)
    description: Mapped[Optional[str]]
    health_based: Mapped[bool] = mapped_column(Boolean, default=False)

    mood: Mapped["Mood"] = relationship(
        back_populates="humor", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Humor(id={self.id!r}, value{self.value!r}, description={self.description!r})"


class Water(Base):
    __tablename__ = "user_water_intake"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.today().date())
    milliliters: Mapped[int]
    description: Mapped[Optional[str]]
    pee: Mapped[bool] = mapped_column(Boolean, default=False)

    mood: Mapped["Mood"] = relationship(
        back_populates="water_intake", cascade="all, delete-orphan"
    )


class Exercises(Base):
    __tablename__ = "user_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.today().date())
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]]

    mood: Mapped["Mood"] = relationship(
        back_populates="exercises", cascade="all, delete-orphan"
    )


class Food(Base):
    __tablename__ = "user_food_habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.today().date())
    value: Mapped[int]
    description: Mapped[str] = mapped_column(String(256))

    mood: Mapped["Mood"] = relationship(
        back_populates="food_habits", cascade="all, delete-orphan"
    )


class Mood(Base):
    __tablename__ = "user_mood"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.today().date())
    humor_id: Mapped[int] = mapped_column(ForeignKey("user_humor.id"))
    water_intake_id: Mapped[int] = mapped_column(ForeignKey("user_water_intake.id"))
    exercises_id: Mapped[int] = mapped_column(ForeignKey("user_exercises.id"))
    food_habits_id: Mapped[int] = mapped_column(ForeignKey("user_food_habits.id"))

    humor: Mapped["Humor"] = relationship(back_populates="mood")
    water_intake: Mapped["Water"] = relationship(back_populates="mood")
    exercises: Mapped["Exercises"] = relationship(back_populates="mood")
    food_habits: Mapped["Food"] = relationship(back_populates="mood")
