import pandas as pd
import numpy as np
from pymongo import MongoClient
import json
import datetime

# MongoDB connection
MONGO_URI = "mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0"

# Timezone Offset
PKT_OFFSET = 5  # Pakistan Time (GMT+5)

def fetch_data():
    """Fetch sensor data from MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client["plantree"]
    collection = db["sensordatas_test"]
    
    # Fetch all documents
    data_cursor = collection.find({})
    data_list = list(data_cursor)
    client.close()
    
    # Convert to DataFrame
    return pd.DataFrame(data_list)

def convert_to_pkt(timestamp):
    """Convert GMT to Pakistan Time (PKT)."""
    return timestamp + pd.Timedelta(hours=PKT_OFFSET)

def create_daily_timeline(day, start_time="03:00", end_time="11:00", freq="5min"):
    """Create a timeline from start_time to end_time (GMT) with 5-min intervals."""
    day = pd.to_datetime(day).normalize()
    start = pd.to_datetime(f"{day.date()} {start_time}")  # GMT
    end = pd.to_datetime(f"{day.date()} {end_time}")  # GMT
    timeline = pd.date_range(start=start, end=end, freq=freq)
    return pd.DataFrame({'timestamp': timeline})

def find_nearest_reading(df, target_time, tolerance="1h"):
    """Find the nearest available reading within the given tolerance."""
    df = df.copy()
    df["time_diff"] = abs(df["timestamp"] - target_time)
    df = df[df["time_diff"] <= pd.Timedelta(tolerance)]  # Filter within tolerance

    if df.empty:
        return None  # No data within tolerance
    return df.loc[df["time_diff"].idxmin()]  # Return closest timestamp data

def fill_location_data_for_day(df_day, df_all, location, tolerance="1h"):
    """Fill missing timestamps for a given location."""
    df_loc = df_day[df_day['location'] == location].copy()
    df_loc.sort_values('timestamp', inplace=True)

    # Create complete timeline for the day
    timeline_df = create_daily_timeline(df_day['timestamp'].min())

    filled_data = []

    for target_time in timeline_df["timestamp"]:
        nearest = find_nearest_reading(df_loc, target_time, tolerance)
        
        if nearest is None:
            df_location_all = df_all[df_all["location"] == location]  # All time data for the location
            
            prev_day_data = df_location_all[df_location_all["timestamp"] < target_time]
            next_day_data = df_location_all[df_location_all["timestamp"] > target_time]
            
            nearest_prev = find_nearest_reading(prev_day_data, target_time, tolerance="3D")
            nearest_next = find_nearest_reading(next_day_data, target_time, tolerance="3D")

            if nearest_prev is not None and nearest_next is not None:
                nearest = nearest_prev if abs(nearest_prev["timestamp"] - target_time) < abs(nearest_next["timestamp"] - target_time) else nearest_next
            else:
                nearest = nearest_prev if nearest_prev is not None else nearest_next
        
        if nearest is not None:
            filled_data.append({
                "timestamp": target_time,
                "location": location,
                "temperature": nearest["temperature"],
                "humidity": nearest["humidity"],
                "mq135": nearest["mq135"]
            })

    return pd.DataFrame(filled_data)

def process_day(df, df_all, day):
    """Process a single day of data."""
    day = pd.to_datetime(day).normalize()
    df_day = df[(df['timestamp'] >= day) & (df['timestamp'] < day + pd.Timedelta(days=1))]

    if df_day.empty:
        return pd.DataFrame()  # Ignore days with no data

    locations = ["New Karachi", "Scheme 33", "Shah Faisal", "Fast Uni"]
    
    filled_list = []
    for loc in locations:
        filled = fill_location_data_for_day(df_day, df_all, loc)
        filled_list.append(filled)

    return pd.concat(filled_list, ignore_index=True)

def main():
    # Fetch data from MongoDB
    df = fetch_data()
    MONGO_URI = "mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(MONGO_URI)
    db = client["plantree"]
    collection = db["sensordatas"]

    # Set the date range for deletion
    start_date = datetime.datetime(2024, 10, 20, 0, 0, 0, tzinfo=datetime.UTC)  # Start of the affected data
    end_date = datetime.datetime(2024, 10, 30, 23, 59, 59, tzinfo=datetime.UTC)  # End of the affected data

    # Delete mistakenly inserted records
    deleted_count = collection.delete_many({
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }).deleted_count

    print(f"✅ Deleted {deleted_count} mistakenly inserted records.")

    client.close()
    # Convert timestamps to datetime format
    # df['timestamp'] = pd.to_datetime(df['timestamp'])
    # df.sort_values('timestamp', inplace=True)

    # # Convert timestamps to PKT (Pakistan Time)
    # df["timestamp"] = df["timestamp"].apply(convert_to_pkt)

    # # Get a list of unique days with at least one sensor reading
    # unique_days = df['timestamp'].dt.normalize().unique()[:15]  # TESTING: Process only the first 15 days

    # # Process each day and fill missing data
    # filled_days = []
    # for day in unique_days:
    #     filled_day = process_day(df, df, day)
    #     if not filled_day.empty:
    #         filled_days.append(filled_day)

    # # Combine all processed days
    # df_filled = pd.concat(filled_days, ignore_index=True)

    # print("Filled Data Sample:\n", df_filled.head())

    # # Save to a local file for verification
    # df_filled.to_json("test_filled_data.json", orient="records")

def insert_all_filled_data():
    """Insert all filled records into MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client["plantree"]
    collection = db["sensordatas"]

    with open("test_filled_data.json") as f:
        filled_data = json.load(f)

    if filled_data:
        collection.insert_many(filled_data)  # ✅ Insert all records
        print(f"Inserted {len(filled_data)} filled records successfully!")
    else:
        print("No new records to insert.")

    client.close()

    """Insert only 10 test records into MongoDB to verify the update works correctly."""
    client = MongoClient(MONGO_URI)
    db = client["plantree"]
    collection = db["sensordatas"]

    with open("test_filled_data.json") as f:
        sample_data = json.load(f)

    # Insert only 10 test records
    collection.insert_many(sample_data[:10])  
    print("Inserted 10 test records successfully!")

    client.close()

if __name__ == '__main__':
    main()
    # insert_all_filled_data()  # Only insert 10 records for safe testing
