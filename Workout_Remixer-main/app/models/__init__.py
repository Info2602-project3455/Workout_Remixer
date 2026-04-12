from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .user import User

class Workout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    category: str
    difficulty: str
    muscle_group: str
    routine_links: List["RoutineWorkout"] = Relationship(back_populates="workout")

class Routine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="routines")
    workouts: List["RoutineWorkout"] = Relationship(back_populates="routine")

class RoutineWorkout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routine.id")
    workout_id: int = Field(foreign_key="workout.id")
    sets: int = Field(default=3)
    reps: int = Field(default=10)
    routine: Optional[Routine] = Relationship(back_populates="workouts")
    workout: Optional[Workout] = Relationship(back_populates="routine_links")