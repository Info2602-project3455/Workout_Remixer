from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models import Routine, RoutineWorkout, Workout
from sqlmodel import select
from . import router, templates


class AddWorkoutRequest(BaseModel):
    workout_id: int
    sets: int = 3
    reps: int = 10

@router.get("/routines", response_class=HTMLResponse)
async def routines_view(request: Request, user: AuthDep, db: SessionDep):
    routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()
    return templates.TemplateResponse(
        request=request,
        name="routines.html",
        context={
            "user": user,
            "routines": routines
        }
    )

@router.get("/routines/{routine_id}/edit", response_class=HTMLResponse)
async def edit_routine_view(routine_id: int, request: Request, user: AuthDep, db: SessionDep):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    # Get all workouts for search/display
    all_workouts = db.exec(select(Workout)).all()
    
    return templates.TemplateResponse(
        request=request,
        name="workouts.html",
        context={
            "user": user,
            "routine": routine,
            "workouts": all_workouts
        }
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

@api_router.delete("/{routine_id}")
async def delete_routine(routine_id: int, db: SessionDep, user: AuthDep):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(routine)
    db.commit()
    return {"message": "Routine deleted"}

@api_router.post("/{routine_id}/workouts")
async def add_workout_to_routine(    
    routine_id:int,
    workout_data: AddWorkoutRequest,
    db: SessionDep,
    user: AuthDep
):
    
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    link = RoutineWorkout(
        routine_id=routine_id,
        workout_id=workout_data.workout_id,
        sets=workout_data.sets,
        reps=workout_data.reps
    )
    db.add(link)
    db.commit()
    return {"message": "Workout added to routine"}

@api_router.delete("/{routine_id}/workouts/{routine_workout_id}")
async def remove_workout_from_routine(routine_id: int, routine_workout_id: int, db: SessionDep, user: AuthDep):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    link = db.get(RoutineWorkout, routine_workout_id)
    if not link or link.routine_id != routine_id:
        raise HTTPException(status_code=404, detail="Not found")
    
    db.delete(link)
    db.commit()
    return {"message": "Workout removed from routine"}