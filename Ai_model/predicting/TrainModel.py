import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def fetch_data():
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas_test"]
    total_docs = collection.count_documents({})
    print(f"Total documents in collection: {total_docs}")

    # Try a looser query to debug
    sample_docs = list(collection.find().limit(5))
    print("Sample document:", sample_docs[0] if sample_docs else "No documents found")

    # Now try a lighter filter to test
    filtered = list(collection.find({"shadeLabel": {"$exists": True}}))
    print(f"Documents with 'shadeLabel': {len(filtered)}")

    client.close()

    df = pd.DataFrame(filtered)
    print("Columns in DataFrame:", df.columns.tolist())
    return df


def train_models_by_location(df):
    os.makedirs("impact_models", exist_ok=True)

    locations = df["location"].unique()
    for loc in locations:
        loc_df = df[df["location"] == loc].copy()
        loc_df["shadeLabel"] = loc_df["shadeLabel"].apply(lambda x: 1 if x.lower() == "shaded" else 0)

        X = loc_df[["shadeLabel", "humidity", "mq135"]]
        
        # Train a model to predict temperature
        temp_model = RandomForestRegressor(n_estimators=100, random_state=42)
        temp_model.fit(X, loc_df["temperature"])
        joblib.dump(temp_model, f"impact_models/{loc}_temperature_model.pkl")

        # Train a model to predict humidity
        hum_model = RandomForestRegressor(n_estimators=100, random_state=42)
        hum_model.fit(X, loc_df["humidity"])
        joblib.dump(hum_model, f"impact_models/{loc}_humidity_model.pkl")

        # Train a model to predict air quality (mq135)
        air_model = RandomForestRegressor(n_estimators=100, random_state=42)
        air_model.fit(X, loc_df["mq135"])
        joblib.dump(air_model, f"impact_models/{loc}_air_model.pkl")

        print(f"✅ Trained & saved models for: {loc}")

def main():
    df = fetch_data()
    train_models_by_location(df)

if __name__ == "__main__":
    main()
