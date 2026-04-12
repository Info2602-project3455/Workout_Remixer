from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router, templates


@router.get("/browse", response_class=HTMLResponse)
async def browse_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="browse.html",
        context={
            "user": user
        }
    )
