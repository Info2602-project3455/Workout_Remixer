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

async def fetch_and_seed():
    typer.echo("Fetching workouts and images from wger API...")
    # 1. We need TWO different URLs
    INFO_URL = "https://wger.de/api/v2/exerciseinfo/?format=json&language=2&limit=500"
    IMAGE_URL = "https://wger.de/api/v2/exerciseimage/?format=json&limit=500"
    
    async with httpx.AsyncClient() as client:
        # 2. Fetch both at the same time
        info_resp, img_resp = await asyncio.gather(
            client.get(INFO_URL),
            client.get(IMAGE_URL)
        )
        
        # 3. Get the 'results' list from both
        exercises = info_resp.json().get("results", [])
        images = img_resp.json().get("results", [])

    # 4. Create a map where key is the Exercise ID and value is the Image URL
    # In the image API, 'exercise_base' is the ID that matches the exercise's 'id'
    image_map = {img["exercise_base"]: img["image"] for img in images if "exercise_base" in img}

    with Session(engine) as db:
        count = 0
        for item in exercises:
            if not item.get("translations"): continue
            
            # Get English name/description
            name, description = None, None
            for t in item["translations"]:
                if t["language"] == 2:
                    name = t["name"]
                    description = t["description"] or "No description"
                    break
            
            if not name: continue

            # 5. CRITICAL: Match the image using the exercise's ID
            # This looks into our map to find the real .png/.jpg link
            image_link = image_map.get(item["id"])
            
            # If no image is found in the map, use the placeholder
            if not image_link:
                image_link = "https://wger.de/static/images/icons/image-placeholder.svg"

            workout = Workout(
                name=name,
                description=description,
                category=item["category"]["name"] if item.get("category") else "General",
                difficulty="Intermediate",
                muscle_group=item["muscles"][0]["name_en"] if item.get("muscles") else "Full Body",
                image_url=image_link  # This now contains the real link!
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