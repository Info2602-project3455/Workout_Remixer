from fastapi import APIRouter, HTTPException, Request, Query
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


class CreateRoutineRequest(BaseModel):
    name: str
    description: str = ""


class UpdateRoutineRequest(BaseModel):
    name: str
    description: str = ""


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
    # Get routine with workouts loaded
    routine = db.exec(
        select(Routine)
        .where(Routine.id == routine_id)
        .where(Routine.user_id == user.id)
    ).first()

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    # Get all workouts for search/display
    all_workouts = db.exec(select(Workout)).all()

    return templates.TemplateResponse(
        request=request,
        name="routines.html",
        context={
            "user": user,
            "routine": routine,
            "workouts": all_workouts,
            "is_edit": True
        }
    )


# API Routes
api_router = APIRouter(prefix="/routines")


@api_router.get("")
async def list_routines(db: SessionDep, user: AuthDep):
    routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()
    return routines


@api_router.post("")
async def create_routine(routine_data: CreateRoutineRequest, db: SessionDep, user: AuthDep):
    routine = Routine(
        name=routine_data.name,
        description=routine_data.description,
        user_id=user.id
    )
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine


@api_router.get("/workouts-search")
async def search_workouts(
    db: SessionDep,
    search: str = Query(None)
):
    query = select(Workout)
    if search:
        query = query.where(Workout.name.ilike(f"%{search}%"))
    workouts = db.exec(query).all()
    return workouts


@api_router.get("/{routine_id}")
async def get_routine(routine_id: int, db: SessionDep, user: AuthDep):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return routine


@api_router.put("/{routine_id}")
async def update_routine(routine_id: int, routine_data: UpdateRoutineRequest, db: SessionDep, user: AuthDep):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    routine.name = routine_data.name
    routine.description = routine_data.description
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine


@api_router.delete("/{routine_id}")
async def delete_routine(routine_id: int, db: SessionDep, user: AuthDep):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    routine_workouts = db.exec(
        select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)
    ).all()

    for routine_workout in routine_workouts:
        db.delete(routine_workout)

    db.delete(routine)
    db.commit()
    return {"message": "Routine deleted"}


@api_router.post("/{routine_id}/workouts")
async def add_workout_to_routine(
    routine_id: int,
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
async def remove_workout_from_routine(
    routine_id: int,
    routine_workout_id: int,
    db: SessionDep,
    user: AuthDep
):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    routine_workout = db.get(RoutineWorkout, routine_workout_id)
    if not routine_workout or routine_workout.routine_id != routine_id:
        raise HTTPException(status_code=404, detail="Workout not found in routine")

    db.delete(routine_workout)
    db.commit()
    return {"message": "Workout removed from routine"}


@api_router.put("/{routine_id}/workouts/{routine_workout_id}")
async def swap_workout_in_routine(
    routine_id: int,
    routine_workout_id: int,
    workout_data: AddWorkoutRequest,
    db: SessionDep,
    user: AuthDep
):
    routine = db.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    routine_workout = db.get(RoutineWorkout, routine_workout_id)
    if not routine_workout or routine_workout.routine_id != routine_id:
        raise HTTPException(status_code=404, detail="Workout not found in routine")

    routine_workout.workout_id = workout_data.workout_id
    routine_workout.sets = workout_data.sets
    routine_workout.reps = workout_data.reps
    db.add(routine_workout)
    db.commit()
    return {"message": "Workout swapped in routine"}


@api_router.get("/{routine_id}/details")
async def get_routine_details(routine_id: int, db: SessionDep, user: AuthDep):
    routine = db.exec(
        select(Routine)
        .where(Routine.id == routine_id)
        .where(Routine.user_id == user.id)
    ).first()

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    return {
        "id": routine.id,
        "name": routine.name,
        "description": routine.description,
        "workouts": [
            {
                "id": rw.id,
                "workout_id": rw.workout_id,
                "workout": {
                    "id": rw.workout.id,
                    "name": rw.workout.name,
                    "description": rw.workout.description,
                    "category": rw.workout.category,
                    "difficulty": rw.workout.difficulty,
                    "muscle_group": rw.workout.muscle_group,
                    "image_url": getattr(rw.workout, "image_url", None)
                },
                "sets": rw.sets,
                "reps": rw.reps
            }
            for rw in routine.workouts
        ]
    }