from pymongo import MongoClient
import datetime

# MongoDB connection
MONGO_URI = "mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["plantree"]

# Collections
source_collection = db["sensordatas"]
target_collection = db["sensordatas_test"]

# Get today's date in UTC
today_start = datetime.datetime.now(datetime.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
today_end = today_start + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

# Fetch today's data
today_data = list(source_collection.find({"timestamp": {"$gte": today_start, "$lte": today_end}}))

if today_data:
    # Remove _id field to avoid duplicate key error
    for doc in today_data:
        doc.pop("_id", None)

    # Insert into target collection
    target_collection.insert_many(today_data)
    print(f"✅ Copied {len(today_data)} records from sensordatas to sensordatas_test.")
else:
    print("⚠️ No records found for today.")

# Close connection
client.close()
