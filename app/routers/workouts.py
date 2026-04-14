from fastapi import APIRouter, HTTPException
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models import Workout
from sqlmodel import select


api_router = APIRouter(prefix="/workouts")

@api_router.get("")
async def list_workouts(db: SessionDep):
    workouts = db.exec(select(Workout)).all()
    return workouts

@api_router.post("")
async def create_workout(workout: Workout, db: SessionDep, user: AuthDep):
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout

@api_router.get("/{workout_id}")
async def get_workout(workout_id: int, db: SessionDep):
    workout = db.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@api_router.delete("/{workout_id}")
async def delete_workout(workout_id: int, db: SessionDep, user: AuthDep):
    workout = db.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()
    return {"message": "Workout deleted"}