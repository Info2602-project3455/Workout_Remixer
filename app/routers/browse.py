from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models import Workout
from sqlmodel import select, func
from . import router, templates
import math

@router.get("/browse", response_class=HTMLResponse)
async def browse_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = 1
):
    # Pagination settings
    items_per_page = 20
    offset = (page - 1) * items_per_page
    
    # Get total count
    total_count = db.exec(select(func.count(Workout.id))).one()
    total_pages = math.ceil(total_count / items_per_page)
    
    # Get paginated workouts
    workouts = db.exec(select(Workout).offset(offset).limit(items_per_page)).all()
    
    return templates.TemplateResponse(
        request=request,
        name="browse.html",
        context={
            "user": user,
            "workouts": workouts,
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "items_per_page": items_per_page
        }
    )