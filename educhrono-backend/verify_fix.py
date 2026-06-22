from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "educhrono")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"Verifying indexes for collection: users")
indexes = db["users"].index_information()
for name, info in indexes.items():
    print(f"Index Name: {name}")
    print(f"  Keys: {info['key']}")
    print(f"  Unique: {info.get('unique', False)}")

# Check for duplicates one more time just to be safe
pipeline = [
    {"$group": {"_id": "$email", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]
duplicates = list(db["users"].aggregate(pipeline))
if not duplicates:
    print("No duplicates found. Index should be active.")
else:
    print(f"Found {len(duplicates)} duplicate emails! Index creation might have failed.")
