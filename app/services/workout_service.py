import httpx

WGER_API_URL = "https://wger.de/api/v2/exerciseinfo/?limit=12"
WGER_BASE_URL = "https://wger.de"


def build_absolute_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{WGER_BASE_URL}{url}"


def pick_translation(item: dict) -> dict:
    translations = item.get("translations", [])
    if not translations:
        return {}

    # Prefer English if present
    for translation in translations:
        if str(translation.get("language")) == "2":
            return translation

    # Otherwise use the first available translation
    return translations[0]


async def fetch_workouts_from_api():
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(WGER_API_URL)
        response.raise_for_status()
        data = response.json()

    workouts = []

    for item in data.get("results", []):
        translation = pick_translation(item)

        category = item.get("category", {})
        if isinstance(category, dict):
            category_name = category.get("name", "Unknown")
        else:
            category_name = "Unknown"

        images = item.get("images", [])
        raw_image_url = None
        if images and isinstance(images[0], dict):
            raw_image_url = images[0].get("image")

        muscles = item.get("muscles", [])
        if muscles and isinstance(muscles[0], dict):
            muscle_group = muscles[0].get("name_en") or muscles[0].get("name") or "Unknown"
        else:
            muscle_group = "Unknown"

        workout_name = (
            translation.get("name")
            or item.get("name")
            or "Unnamed Workout"
        )

        workout_description = (
            translation.get("description")
            or item.get("description")
            or "No description available"
        )

        workouts.append({
            "name": workout_name,
            "description": workout_description,
            "category": category_name,
            "difficulty": "Unknown",
            "muscle_group": muscle_group,
            "image_url": build_absolute_url(raw_image_url),
        })

    return workouts