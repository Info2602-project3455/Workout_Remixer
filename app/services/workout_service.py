import httpx

API_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
IMAGE_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"

async def fetch_workouts_from_api():
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(API_URL)
        response.raise_for_status()
        data = response.json()

    workouts = []

    for item in data:
        name = item.get("name")
        if not name:
            continue

        # Combine instructions into one description
        instructions = item.get("instructions", [])
        description = " ".join(instructions) if instructions else "No description available"

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

        workouts.append({
            "name": name,
            "description": description,
            "category": category,
            "difficulty": difficulty,
            "muscle_group": muscle_group,
            "image_url": image_url,
        })

    return workouts