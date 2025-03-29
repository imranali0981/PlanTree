import pandas as pd
import joblib
from pymongo import MongoClient

# Load trained model
rf = joblib.load("random_forest_label_model.pkl")

# Connect to MongoDB
client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
db = client["plantree"]
collection = db["sensordatas_test"]

# Fetch latest data
data_cursor = collection.find({})
data_list = list(data_cursor)
df = pd.DataFrame(data_list)

# Drop MongoDB _id column (not needed for ML)
df.drop(columns=['_id'], inplace=True, errors='ignore')

# Drop missing values (if any)
df.dropna(inplace=True)

# Select features
X = df[['temperature', 'humidity', 'mq135']]

# Predict plantation need (1 = Needs Plantation, 0 = Doesn't)
df['plantation_needed'] = rf.predict(X)

# Count plantation needs per location
location_counts = df[df['plantation_needed'] == 1]['location'].value_counts()

# Find the area with the most need
most_needed_area = location_counts.idxmax()
most_needed_count = location_counts.max()

# Print detailed results
print(f"🌱 The area most in need of tree plantation is: **{most_needed_area}**")
print(f"📊 Number of times this area was marked for plantation: **{most_needed_count}**")

# Print all areas with plantation need counts
print("\n📌 Plantation Need Count Per Area:")
for location, count in location_counts.items():
    print(f"- {location}: {count} times")

