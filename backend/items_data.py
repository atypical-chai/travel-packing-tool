"""
Seed data for the Travel Packing List backend.
Items with category (pack/buy/do) and tags: base, work, outdoor, roadtrip, hot, cold, rain,
laptop, camera, beach, fitness, international, downtime.
Run this after database.py to populate items_master.
"""
from database import init_database, seed_database

ITEMS = [
    # --- Base (pack) ---
    {"name": "Upper wear", "category": "pack", "tags": ["base"]},
    {"name": "Bottom wear", "category": "pack", "tags": ["base"]},
    {"name": "Sleeping wear", "category": "pack", "tags": ["base"]},
    {"name": "Undergarments", "category": "pack", "tags": ["base"]},
    {"name": "Socks", "category": "pack", "tags": ["base"]},
    {"name": "Belt", "category": "pack", "tags": ["base"]},
    {"name": "Main shoes", "category": "pack", "tags": ["base"]},
    {"name": "Sandals / home footwear", "category": "pack", "tags": ["base"]},
    {"name": "Face wash", "category": "pack", "tags": ["base"]},
    {"name": "Body wash / soap", "category": "pack", "tags": ["base"]},
    {"name": "Shampoo", "category": "pack", "tags": ["base"]},
    {"name": "Toothbrush", "category": "pack", "tags": ["base"]},
    {"name": "Toothpaste", "category": "pack", "tags": ["base"]},
    {"name": "Moisturiser", "category": "pack", "tags": ["base"]},
    {"name": "Sunscreen", "category": "pack", "tags": ["base"]},
    {"name": "Serum", "category": "pack", "tags": ["base"]},
    {"name": "Comb / hair brush", "category": "pack", "tags": ["base"]},
    {"name": "Medications", "category": "pack", "tags": ["base"]},
    {"name": "Phone charger", "category": "pack", "tags": ["base"]},
    {"name": "Power bank", "category": "pack", "tags": ["base", "camera"]},
    {"name": "Sunglasses", "category": "pack", "tags": ["base"]},
    {"name": "Earphones / headphones", "category": "pack", "tags": ["base"]},
    {"name": "Speaker", "category": "pack", "tags": ["base"]},
    {"name": "Travel towel", "category": "pack", "tags": ["base"]},
    {"name": "Wallet / cash", "category": "pack", "tags": ["base"]},
    # --- Base (buy) ---
    {"name": "Sanitiser", "category": "buy", "tags": ["base"]},
    {"name": "Bandages / basic first aid", "category": "buy", "tags": ["base"]},
    # --- Base (do) ---
    {"name": "Keep valid photo ID handy", "category": "do", "tags": ["base"]},
    {"name": "Close / lock home", "category": "do", "tags": ["base"]},
    {"name": "Charge devices", "category": "do", "tags": ["base"]},
    {"name": "Download songs / movies for commute", "category": "do", "tags": ["base"]},
    {"name": "Confirm hotel booking", "category": "do", "tags": ["base"]},
    # --- Work (Laptop & charger in laptop section with work tag) ---
    {"name": "Work clothes", "category": "pack", "tags": ["work"]},
    {"name": "Confirm work setup / internet if needed", "category": "do", "tags": ["work"]},
    {"name": "Set out of office / out of station", "category": "do", "tags": ["work"]},
    # --- Outdoor / trek ---
    {"name": "Raincoat", "category": "pack", "tags": ["outdoor", "rain"]},
    {"name": "Trekking shoes", "category": "pack", "tags": ["outdoor"]},
    {"name": "Regular carry bag", "category": "pack", "tags": ["outdoor"]},
    {"name": "Waterproof bag", "category": "pack", "tags": ["outdoor", "rain"]},
    {"name": "Polythene bags / wet bags", "category": "pack", "tags": ["outdoor", "rain"]},
    {"name": "Headlamp / torch", "category": "pack", "tags": ["outdoor"]},
    {"name": "Mosquito repellent", "category": "pack", "tags": ["outdoor"]},
    {"name": "Protein bars", "category": "buy", "tags": ["outdoor", "fitness"]},
    # --- Road trip (planned activity) ---
    {"name": "Road trip snacks", "category": "buy", "tags": ["roadtrip"]},
    {"name": "Create road trip playlist", "category": "do", "tags": ["roadtrip"]},
    {"name": "Fuel up your car", "category": "do", "tags": ["roadtrip"]},
    {"name": "Confirm car rental / cab booking if needed", "category": "do", "tags": ["roadtrip"]},
    {"name": "Download offline maps", "category": "do", "tags": ["roadtrip"]},
    # --- Hot ---
    {"name": "Shorts", "category": "pack", "tags": ["hot"]},
    {"name": "Hat / cap", "category": "pack", "tags": ["hot"]},
    {"name": "Deodorant", "category": "pack", "tags": ["hot"]},
    {"name": "Small towel / handkerchief", "category": "pack", "tags": ["hot"]},
    # --- Cold ---
    {"name": "Jacket / hoodie", "category": "pack", "tags": ["cold"]},
    {"name": "Woolen socks", "category": "pack", "tags": ["cold"]},
    {"name": "Thermals / body warmers", "category": "pack", "tags": ["cold"]},
    {"name": "Warm layers", "category": "pack", "tags": ["cold"]},
    {"name": "Gloves", "category": "pack", "tags": ["cold"]},
    {"name": "Scarf", "category": "pack", "tags": ["cold"]},
    {"name": "Winter cap / beanie", "category": "pack", "tags": ["cold"]},
    # --- Rain (Raincoat, Waterproof bag, Polythene bags already in outdoor) ---
    {"name": "Quick-dry clothes", "category": "pack", "tags": ["rain"]},
    {"name": "Umbrella", "category": "pack", "tags": ["rain"]},
    # --- Laptop (extra gear; also used by work) ---
    {"name": "Laptop", "category": "pack", "tags": ["work", "laptop"]},
    {"name": "Laptop charger", "category": "pack", "tags": ["work", "laptop"]},
    {"name": "Laptop sleeve / bag", "category": "pack", "tags": ["laptop"]},
    # --- Camera gear ---
    {"name": "Camera", "category": "pack", "tags": ["camera"]},
    {"name": "Memory card", "category": "pack", "tags": ["camera"]},
    {"name": "Charging cable", "category": "pack", "tags": ["camera"]},
    {"name": "Camera stand", "category": "pack", "tags": ["camera"]},
    # --- Beach / water activities ---
    {"name": "Swimwear", "category": "pack", "tags": ["beach"]},
    {"name": "Crocs / sandals", "category": "pack", "tags": ["beach"]},
    {"name": "Towel", "category": "pack", "tags": ["beach", "fitness"]},
    # --- Fitness / workout (Protein bars already in outdoor) ---
    {"name": "Workout clothes", "category": "pack", "tags": ["fitness"]},
    {"name": "Sports shoes", "category": "pack", "tags": ["fitness"]},
    # --- International ---
    {"name": "Passport", "category": "pack", "tags": ["international"]},
    {"name": "Travel cards / lounge card", "category": "pack", "tags": ["international"]},
    {"name": "Currency exchange / forex", "category": "buy", "tags": ["international"]},
    {"name": "Travel adapter", "category": "buy", "tags": ["international"]},
    {"name": "Check passport validity", "category": "do", "tags": ["international"]},
    {"name": "Arrange currency exchange", "category": "do", "tags": ["international"]},
    {"name": "Arrange international driving permit if needed", "category": "do", "tags": ["international"]},
    {"name": "Arrange eSIM / local SIM or roaming", "category": "do", "tags": ["international"]},
    {"name": "Check visa requirements", "category": "do", "tags": ["international"]},
    # --- Downtime (planned activity) ---
    {"name": "Books", "category": "pack", "tags": ["downtime"]},
    {"name": "Journaling", "category": "pack", "tags": ["downtime"]},
    {"name": "Art kit", "category": "pack", "tags": ["downtime"]},
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
