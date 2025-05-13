from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["plantree"]

# Collections
source_collection = db["sensordatas"]
target_collection = db["sensordatas_test"]

# Fetch all documents
all_data = list(source_collection.find())

if all_data:
    # Remove _id field to avoid duplicate key error
    for doc in all_data:
        doc.pop("_id", None)

    # Insert into target collection
    target_collection.insert_many(all_data)
    print(f"✅ Copied {len(all_data)} records from sensordatas to sensordatas_test.")
else:
    print("⚠️ No records found in source collection.")

# Close connection
client.close()
