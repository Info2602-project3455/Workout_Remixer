from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models import Routine, RoutineWorkout, Workout
from sqlmodel import select
from . import router, templates

@router.get("/routines", response_class=HTMLResponse)
async def routines_view(request: Request, user: AuthDep, db: SessionDep):
    return templates.TemplateResponse(
        request=request,
        name="routines.html",
        context={"user": user}
    )

api_router = APIRouter(prefix="/routines")

@api_router.get("")
async def list_routines(db: SessionDep, user: AuthDep):
    routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()
    return routines

@api_router.post("")
async def create_routine(routine: Routine, db: SessionDep, user: AuthDep):
    routine.user_id = user.id
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine

@api_router.get("/{routine_id}")
async def get_routine(routine_id: int, db: SessionDep, user: AuthDep):
    routine = db.get(Routine, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return routine

@api_router.post("/{routine_id}/workouts")
async def add_workout_to_routine(routine_id: int, workout_id: int, sets: int, reps: int, db: SessionDep, user: AuthDep):
    routine = db.get(Routine, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    link = RoutineWorkout(routine_id=routine_id, workout_id=workout_id, sets=sets, reps=reps)
    db.add(link)
    db.commit()
    return {"message": "Workout added to routine"}

@api_router.delete("/{routine_id}/workouts/{workout_id}")
async def remove_workout_from_routine(routine_id: int, workout_id: int, db: SessionDep, user: AuthDep):
    link = db.exec(select(RoutineWorkout).where(
        RoutineWorkout.routine_id == routine_id,
        RoutineWorkout.workout_id == workout_id
    )).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(link)
    db.commit()
    return {"message": "Workout removed from routine"}