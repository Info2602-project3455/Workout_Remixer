from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from app.models import Workout
from sqlmodel import select
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    workouts = db.exec(select(Workout)).all()
    return templates.TemplateResponse(
        request=request, 
        name="app.html",
        context={
            "user": user,
            "workouts": workouts
        }
    )