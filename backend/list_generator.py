"""
Core logic: generate a personalized packing checklist from trip details.
Uses base + addons (tags) → query DB → dedupe → group by category → sort.
"""
from database import get_items_by_tags


def generate_checklist(trip_type, travelling_with, season):
    """
    Build tags from trip details, fetch matching items, dedupe, group, sort.
    Returns: {"pack": [{"text": "...", "completed": false}, ...], "buy": [...], "do": [...]}
    """
    # 1. Build tags list: base + trip_type + travelers (exclude "me") + season
    tags = ["base", trip_type]
    for t in travelling_with:
        if t != "me":
            tags.append(t)
    tags.append(season)

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
        ("leisure", ["me"], "summer"),
        ("trek", ["me", "partner", "kids"], "winter"),
    ]

    for trip_type, travelling_with, season in test_cases:
        tags = ["base", trip_type]
        for t in travelling_with:
            if t != "me":
                tags.append(t)
        tags.append(season)

        print(f"\nGenerating checklist for tags: {tags}")

        # Get raw count before deduplication
        raw = get_items_by_tags(tags)
        print(f"Found {len(raw)} items before deduplication")

        result = generate_checklist(trip_type, travelling_with, season)
        total_unique = len(result["pack"]) + len(result["buy"]) + len(result["do"])
        print(f"After deduplication: {total_unique} unique items")

        pack = len(result["pack"])
        buy = len(result["buy"])
        do = len(result["do"])
        print(f"Final counts - Pack: {pack}, Buy: {buy}, Do: {do}")

        # Sanity: trek should have hiking boots, kids should have diapers
        if trip_type == "trek" and "kids" in travelling_with:
            pack_texts = [x["text"] for x in result["pack"]]
            if "Hiking boots" in pack_texts:
                print("  [OK] Trek: Hiking boots present")
            if "Diapers and wipes" in pack_texts:
                print("  [OK] Kids: Diapers present")

    print("\nDone.")
