import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Connect to MongoDB
client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
db = client["plantree"]
collection = db["sensordatas"]

# Fetch Data from MongoDB
data_cursor = collection.find({})
data_list = list(data_cursor)
df = pd.DataFrame(data_list)

# Drop MongoDB _id column (not needed for ML)
df.drop(columns=['_id'], inplace=True, errors='ignore')

# Drop missing values (if any)
df.dropna(inplace=True)

# Select features (we are NOT using cluster as feature!)
X = df[['temperature', 'humidity', 'mq135']]
y = (df['cluster'] == 2).astype(int)  # If cluster = 2 → Needs Plantation (1), Otherwise (0)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Save the trained model
joblib.dump(rf, "random_forest_label_model.pkl")
print("Labeling model saved as random_forest_label_model.pkl")

