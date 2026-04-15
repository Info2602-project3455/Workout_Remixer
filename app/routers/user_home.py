from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlmodel import select, func, or_
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models import Workout
from . import router, templates
import math


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = 1,
    search: str = "",
    category: str = ""
):
    items_per_page = 12

    query = select(Workout)
    count_query = select(func.count(Workout.id))

    # Search across multiple fields
    if search:
        search_term = f"%{search}%"
        search_filter = or_(
            Workout.name.ilike(search_term),
            Workout.description.ilike(search_term),
            Workout.category.ilike(search_term),
            Workout.muscle_group.ilike(search_term)
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Keep your original category groups
    if category:
        category_lower = category.lower()

        category_map = {
            "arms": ["biceps", "triceps", "forearms"],
            "chest": ["chest", "pectorals"],
            "back": ["lats", "middle back", "lower back", "traps", "back"],
            "legs": ["quadriceps", "hamstrings", "glutes", "calves", "adductors", "abductors", "legs"],
            "cardio": ["cardio"],
            "abs": ["abdominals", "abs", "core"],
            "shoulders": ["shoulders", "delts"],
            "calves": ["calves"]
        }

        if category_lower in category_map:
            values = category_map[category_lower]

            category_filter = or_(
                *[Workout.muscle_group.ilike(f"%{value}%") for value in values],
                *[Workout.category.ilike(f"%{value}%") for value in values],
                *[Workout.description.ilike(f"%{value}%") for value in values]
            )

            query = query.where(category_filter)
            count_query = count_query.where(category_filter)

    total_count = db.exec(count_query).one()
    total_pages = math.ceil(total_count / items_per_page) if total_count > 0 else 1

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * items_per_page

    workouts = db.exec(
        query.offset(offset).limit(items_per_page)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "workouts": workouts,
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "items_per_page": items_per_page,
            "search": search,
            "selected_category": category
        }
    )