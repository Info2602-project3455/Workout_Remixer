from fastapi import APIRouter, Depends, HTTPException
from httpx import request
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models import Workout
from sqlmodel import Session, select
from . import templates
from app.database import get_db


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

# app/routers/workouts.py
@api_router.get("/browse")
def browse_workouts(db: Session = Depends(get_db)):
    workouts = db.exec(select(Workout)).all()
    return templates.TemplateResponse("browse.html", {"request": request, "workouts": workouts})