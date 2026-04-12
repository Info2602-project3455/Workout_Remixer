from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router, templates


@router.get("/routines", response_class=HTMLResponse)
async def routines_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="routines.html",
        context={
            "user": user
        }
    )
