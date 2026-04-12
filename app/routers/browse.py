from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models import Workout
from sqlmodel import select
from . import router, templates

@router.get("/browse", response_class=HTMLResponse)
async def browse_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    workouts = db.exec(select(Workout)).all()
    return templates.TemplateResponse(
        request=request,
        name="browse.html",
        context={
            "user": user,
            "workouts": workouts
        }
    )