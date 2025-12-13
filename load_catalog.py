from pymongo import MongoClient
from pymongo.server_api import ServerApi

URI = "mongodb+srv://"

client = MongoClient(URI, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("✅ Conectado ao MongoDB com sucesso!")
except Exception as e:
    print("❌ Erro ao conectar no MongoDB:", e)
    exit()

db = client["Caixa"]
catalog_collection = db["catalog"]

products = [
    {"name": "beet", "display_name": "Beterraba", "price_per_kg": 4.50},
    {"name": "bell_pepper", "display_name": "Pimentão", "price_per_kg": 8.90},
    {"name": "cabbage", "display_name": "Repolho", "price_per_kg": 3.80},
    {"name": "carrot", "display_name": "Cenoura", "price_per_kg": 3.20},
    {"name": "cucumber", "display_name": "Pepino", "price_per_kg": 4.10},
    {"name": "egg", "display_name": "Ovo", "price_per_kg": 12.00},
    {"name": "eggplant", "display_name": "Berinjela", "price_per_kg": 5.60},
    {"name": "garlic", "display_name": "Alho", "price_per_kg": 15.00},
    {"name": "onion", "display_name": "Cebola", "price_per_kg": 3.90},
    {"name": "potato", "display_name": "Batata", "price_per_kg": 2.80},
    {"name": "tomato", "display_name": "Tomate", "price_per_kg": 5.70},
    {"name": "zucchini", "display_name": "Abobrinha", "price_per_kg": 6.10},
]

inserted = 0
updated = 0

for product in products:
    result = catalog_collection.update_one(
        {"name": product["name"]},
        {"$setOnInsert": product},
        upsert=True
    )

    if result.upserted_id:
        inserted += 1
    else:
        updated += 1

print(f" Produtos inseridos: {inserted}")
print(f" Produtos já existentes: {updated}")

catalog_collection.create_index("name", unique=True)

