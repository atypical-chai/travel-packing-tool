"""
Core logic: generate a personalized packing checklist from trip details.
Uses base + addons (tags) → query DB → dedupe → group by category → sort.
"""
from database import get_items_by_tags


def generate_checklist(trip_type, weather, gear, activities, trip_scope):
    """
    Build tags from trip details, fetch matching items, dedupe, group, sort.
    trip_type: general | work | outdoor | roadtrip (general adds no extra tag)
    weather: list of hot, cold, rain
    gear: list of laptop, camera
    activities: list of beach, fitness
    trip_scope: domestic | international (domestic adds no extra tag)
    Returns: {"pack": [...], "buy": [...], "do": [...]}
    """
    # 1. Build tags: base + trip_type (skip "general") + weather + gear + activities + international
    tags = ["base"]
    if trip_type and trip_type != "general":
        tags.append(trip_type)
    tags.extend(weather or [])
    tags.extend(gear or [])
    tags.extend(activities or [])
    if trip_scope == "international":
        tags.append("international")

    # 2. Query database for matching items
    matching = get_items_by_tags(tags)

    # 3. Deduplicate by item name (keep first occurrence)
    unique_by_name = {}
    for item in matching:
        name = item["name"]
        if name not in unique_by_name:
            unique_by_name[name] = item

    unique_items = list(unique_by_name.values())

    # 4. Group by category
    result = {"pack": [], "buy": [], "do": []}
    for item in unique_items:
        cat = item["category"]
        if cat in result:
            result[cat].append({"text": item["name"], "completed": False})

    # 5. Sort each category alphabetically by text
    for cat in result:
        result[cat].sort(key=lambda x: x["text"].lower())

    return result


if __name__ == "__main__":
    # Test with different combinations
    test_cases = [
        ("general", [], [], [], "domestic"),
        ("work", ["hot"], ["laptop"], [], "international"),
        ("outdoor", ["cold", "rain"], [], ["fitness"], "domestic"),
    ]
    for trip_type, weather, gear, activities, trip_scope in test_cases:
        result = generate_checklist(trip_type, weather, gear, activities, trip_scope)
        total = len(result["pack"]) + len(result["buy"]) + len(result["do"])
        print(f"trip_type={trip_type}, weather={weather}, gear={gear}, activities={activities}, scope={trip_scope} -> {total} items")
    print("Done.")
