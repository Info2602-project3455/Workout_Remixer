from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router, templates
from app.services.workout_service import fetch_workouts_from_api


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    workouts = await fetch_workouts_from_api()

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "workouts": workouts
        }
    )