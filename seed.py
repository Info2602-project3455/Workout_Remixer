import httpx
import asyncio
from sqlmodel import Session
from app.database import engine
from app.models import Workout

API_URL = "https://wger.de/api/v2/exerciseinfo/?format=json&language=2&limit=20"

async def seed_workouts():
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL)
        data = response.json()

    with Session(engine) as db:
        for item in data["results"]:
            # Skip if no name
            if not item.get("translations"):
                continue
            
            # Get english translation
            name = None
            description = None
            for t in item["translations"]:
                if t["language"] == 2:  # 2 = English
                    name = t["name"]
                    description = t["description"] or "No description"
                    break
            
            if not name:
                continue

            # Get category
            category = item["category"]["name"] if item.get("category") else "General"
            
            # Get muscle group
            muscles = item.get("muscles", [])
            muscle_group = muscles[0]["name_en"] if muscles else "Full Body"

            # Check if workout already exists
            existing = db.exec(
                __import__("sqlmodel").select(Workout).where(Workout.name == name)
            ).first()
            if existing:
                continue

            workout = Workout(
                name=name,
                description=description,
                category=category,
                difficulty="Intermediate",
                muscle_group=muscle_group
            )
            db.add(workout)
        
        db.commit()
        print("✅ Workouts seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_workouts())