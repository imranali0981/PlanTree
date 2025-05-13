import joblib
import pandas as pd
import requests
from pymongo import MongoClient

def predict_impact(location, current_temp, current_humidity, current_mq135):
    try:
        # Load models
        temp_model = joblib.load(f"impact_models/{location}_temperature_model.pkl")
        hum_model = joblib.load(f"impact_models/{location}_humidity_model.pkl")
        air_model = joblib.load(f"impact_models/{location}_air_model.pkl")
    except FileNotFoundError:
        print(f"❌ No trained models found for location: {location}")
        return

    # Input = assume tree is planted => shadeLabel = 1
    input_data = pd.DataFrame([[1, current_humidity, current_mq135]],
                              columns=["shadeLabel", "humidity", "mq135"])

    predicted_temp = temp_model.predict(input_data)[0]
    predicted_humidity = hum_model.predict(input_data)[0]
    predicted_air = air_model.predict(input_data)[0]

    print(f"\n📍 Location: {location}")
    print(f"🌡️ Current Temp: {current_temp}°C → 🌳 Shaded: {predicted_temp:.2f}°C")
    print(f"💧 Current Humidity: {current_humidity}% → 🌳 Shaded: {predicted_humidity:.2f}%")
    print(f"🌫️ Current Air Quality: {current_mq135} → 🌳 Shaded: {predicted_air:.2f} (mq135)\n")


def get_most_needed_location():
    try:
        res = requests.get("https://haseebkhan09876-plantation-predictor.hf.space/predict_plantation")
        data = res.json()
        most_needed_area = data["result"]["most_needed_area"]
        return most_needed_area
    except Exception as e:
        print(f"❌ Error fetching most needed location: {e}")
        return None


def get_latest_data(location):
    try:
        # Connect to MongoDB Atlas (change URI if you're using local MongoDB)
        client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
        db = client["plantree"]
        collection = db["sensordatas"]

        latest = collection.find({"location": location}).sort("timestamp", -1).limit(1)
        latest_doc = list(latest)

        if not latest_doc:
            print(f"❌ No data found for location: {location}")
            return None

        data = latest_doc[0]
        return {
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "mq135": data["mq135"]
        }

    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return None


# Example usage
if __name__ == "__main__":
    print("Fetching most needed location...")
    location = get_most_needed_location()

    if location:
        print(f"✅ Most needed area: {location}")
        latest = get_latest_data(location)
        if latest:
            predict_impact(
                location=location,
                current_temp=latest["temperature"],
                current_humidity=latest["humidity"],
                current_mq135=latest["mq135"]
            )
    else:
        print("⚠️ Cannot proceed without most needed location.")
