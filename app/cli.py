import typer
import asyncio
import httpx
import uvicorn
from sqlmodel import select, Session, SQLModel
from app.database import create_db_and_tables, engine, drop_all
from app.models import Workout
from app.config import get_settings

cli = typer.Typer()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

async def seed_default_users():
    """Seed default users (bob/bobpass) to database."""
    from app.models.user import User
    from app.utilities.security import encrypt_password
    
    with Session(engine) as db:
        # Check if bob user already exists
        existing_bob = db.exec(select(User).where(User.username == "bob")).one_or_none()
        if existing_bob:
            typer.echo("User 'bob' already exists, skipping...")
            return
        
        # Create bob user
        bob = User(
            username="bob",
            email="bob@example.com",
            password=encrypt_password("bobpass"),
            role="user"
        )
        db.add(bob)
        db.commit()
        typer.secho(f"Successfully created user 'bob' with password 'bobpass'", fg=typer.colors.GREEN)

async def fetch_and_seed():
    typer.echo("Fetching workouts from new API...")

    API_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
    IMAGE_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL)
        exercises = response.json()

    with Session(engine) as db:
        count = 0

        for item in exercises:
            name = item.get("name")
            if not name:
                continue

            # Combine instructions into one string
            instructions = item.get("instructions", [])
            description = " ".join(instructions) if instructions else "No description"

            # Map fields safely
            category = item.get("category", "General")
            difficulty = item.get("level", "Unknown")

            muscles = item.get("primaryMuscles", [])
            muscle_group = muscles[0] if muscles else "Full Body"

            # Build image URL
            images = item.get("images", [])
            if images:
                image_url = IMAGE_BASE + images[0]
            else:
                image_url = None

            workout = Workout(
                name=name,
                description=description,
                category=category,
                difficulty=difficulty,
                muscle_group=muscle_group,
                image_url=image_url
            )

            db.add(workout)
            count += 1

        db.commit()
        typer.secho(f"Successfully added {count} workouts", fg=typer.colors.GREEN)
        
@cli.command()
def initialize():
    """Create tables and seed initial workout data."""
    typer.echo("Initializing Database...")
    create_db_and_tables()
    asyncio.run(seed_default_users())
    asyncio.run(fetch_and_seed())

@cli.command()
def reset():
    """Drop all tables and re-initialize (WARNING: DELETES DATA)."""
    if typer.confirm("Are you sure you want to wipe the database?"):
        drop_all()
        initialize()

@cli.command()
def run():
    """Run the FastAPI development server."""
    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)

if __name__ == "__main__":
    cli()
    
def reset_database_properly():
    print("Connecting to database...")
    # This deletes the OLD table structure
    Workout.__table__.drop(engine, checkfirst=True)
    print("Old workout table dropped.")
    
    # This creates the NEW table structure (including image_url)
    SQLModel.metadata.create_all(engine)
    print("New workout table created with image_url column!")

if __name__ == "__main__":
    reset_database_properly()