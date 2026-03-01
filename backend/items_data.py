"""
Seed data for the Travel Packing List backend.
~50 items with category (pack/buy/do) and tags (base, trek, leisure, etc.).
Run this after database.py to populate items_master.
"""
from database import init_database, seed_database

ITEMS = [
    # --- Base (~16 items) ---
    {"name": "Passport", "category": "pack", "tags": ["base"]},
    {"name": "Clothes", "category": "pack", "tags": ["base"]},
    {"name": "Underwear", "category": "pack", "tags": ["base"]},
    {"name": "Socks", "category": "pack", "tags": ["base"]},
    {"name": "Toiletries", "category": "pack", "tags": ["base"]},
    {"name": "Phone charger", "category": "pack", "tags": ["base"]},
    {"name": "Documents", "category": "pack", "tags": ["base"]},
    {"name": "Medications", "category": "pack", "tags": ["base"]},
    {"name": "Cash and cards", "category": "pack", "tags": ["base"]},
    {"name": "Comfortable shoes", "category": "pack", "tags": ["base"]},
    {"name": "Travel adapter", "category": "buy", "tags": ["base"]},
    {"name": "Sunscreen", "category": "buy", "tags": ["base"]},
    {"name": "Travel insurance", "category": "buy", "tags": ["base"]},
    {"name": "Book flights", "category": "do", "tags": ["base"]},
    {"name": "Reserve hotel", "category": "do", "tags": ["base"]},
    {"name": "Check passport expiry", "category": "do", "tags": ["base"]},
    # --- Trek (~8 items) ---
    {"name": "Hiking boots", "category": "pack", "tags": ["trek"]},
    {"name": "Backpack (40-60L)", "category": "pack", "tags": ["trek"]},
    {"name": "Rain jacket", "category": "pack", "tags": ["trek"]},
    {"name": "Water bottle", "category": "pack", "tags": ["trek"]},
    {"name": "Trekking poles", "category": "buy", "tags": ["trek"]},
    {"name": "Hiking socks", "category": "buy", "tags": ["trek"]},
    {"name": "Check trail conditions", "category": "do", "tags": ["trek"]},
    {"name": "Book permits if needed", "category": "do", "tags": ["trek"]},
    # --- Leisure (~5 items) ---
    {"name": "Camera", "category": "pack", "tags": ["leisure"]},
    {"name": "Sunglasses", "category": "pack", "tags": ["leisure"]},
    {"name": "Book or e-reader", "category": "pack", "tags": ["leisure"]},
    {"name": "Research restaurants", "category": "do", "tags": ["leisure"]},
    {"name": "Book tours", "category": "do", "tags": ["leisure"]},
    # --- Work (~5 items) ---
    {"name": "Laptop and charger", "category": "pack", "tags": ["work"]},
    {"name": "Business cards", "category": "pack", "tags": ["work"]},
    {"name": "Formal clothes", "category": "pack", "tags": ["work"]},
    {"name": "Confirm meetings", "category": "do", "tags": ["work"]},
    # --- Backpacking (~4 items) ---
    {"name": "Sleeping bag", "category": "pack", "tags": ["backpacking"]},
    {"name": "Padlock for lockers", "category": "pack", "tags": ["backpacking"]},
    {"name": "Book hostels", "category": "do", "tags": ["backpacking"]},
    # --- Kids (~5 items) ---
    {"name": "Diapers and wipes", "category": "pack", "tags": ["kids"]},
    {"name": "Kids medications", "category": "pack", "tags": ["kids"]},
    {"name": "Toys", "category": "pack", "tags": ["kids"]},
    {"name": "Snacks for kids", "category": "buy", "tags": ["kids"]},
    # --- Partner (~2 items) ---
    {"name": "Nice outfit for romantic dinner", "category": "pack", "tags": ["partner"]},
    {"name": "Book romantic restaurant", "category": "do", "tags": ["partner"]},
    # --- Parents (~2 items) ---
    {"name": "Book accessible accommodation", "category": "do", "tags": ["parents"]},
    {"name": "Plan rest days", "category": "do", "tags": ["parents"]},
    # --- Summer (~3 items) ---
    {"name": "Swimsuit", "category": "pack", "tags": ["summer"]},
    {"name": "Hat", "category": "pack", "tags": ["summer"]},
    {"name": "Sunscreen SPF 50+", "category": "buy", "tags": ["summer"]},
    # --- Winter (~4 items) ---
    {"name": "Winter coat", "category": "pack", "tags": ["winter"]},
    {"name": "Gloves", "category": "pack", "tags": ["winter"]},
    {"name": "Scarf", "category": "pack", "tags": ["winter"]},
    # --- Autumn/Spring (~2 items) ---
    {"name": "Umbrella", "category": "pack", "tags": ["autumn", "spring"]},
    {"name": "Light jacket", "category": "pack", "tags": ["autumn", "spring"]},
]

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Seeding database with items...")
    seed_database(ITEMS)

    pack = sum(1 for i in ITEMS if i["category"] == "pack")
    buy = sum(1 for i in ITEMS if i["category"] == "buy")
    do = sum(1 for i in ITEMS if i["category"] == "do")
    total = len(ITEMS)

    print(f"Database seeded with {total} items:")
    print(f"  - pack: {pack} items")
    print(f"  - buy: {buy} items")
    print(f"  - do: {do} items")
