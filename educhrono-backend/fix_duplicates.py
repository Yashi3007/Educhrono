from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "educhrono")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"Cleaning up duplicate emails in {DB_NAME}.users...")

# 1. Find duplicates
pipeline = [
    {"$group": {"_id": "$email", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
    {"$match": {"count": {"$gt": 1}}}
]

duplicates = list(db["users"].aggregate(pipeline))

if not duplicates:
    print("No duplicate emails found.")
else:
    for dup in duplicates:
        email = dup["_id"]
        ids = dup["ids"]
        print(f"Found {len(ids)} documents for email: {email}")
        
        # Keep the first one, delete the rest
        to_delete = ids[1:]
        result = db["users"].delete_many({"_id": {"$in": to_delete}})
        print(f"  Deleted {result.deleted_count} duplicates for {email}")

# 2. Create Unique Index on Email
print("Creating unique index on 'email' field...")
try:
    db["users"].create_index("email", unique=True)
    print("✅ Unique index created successfully!")
except Exception as e:
    print(f"❌ Failed to create index: {e}")

# 3. Check current status
print("\nCurrent Indexes on 'users':")
for name, info in db["users"].index_information().items():
    print(f" - {name}: unique={info.get('unique', False)}")
