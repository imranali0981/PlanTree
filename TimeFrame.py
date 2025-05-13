import numpy as np
import pandas as pd
from pymongo import MongoClient

def round_to_nearest_interval(dt, interval_minutes=5):
     # Convert datetime to seconds since epoch (as integer)
    seconds = dt.value // 10**9
    #  determine the interval in seconds
    interval = interval_minutes * 60
    # rounde the seconds to nearest muliple of interval
    rounded_seconds = int(round(seconds/interval)*interval)
    # return the rounded datetime back to datetime format
    return pd.to_datetime(rounded_seconds, unit='s')

def main():
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas"]
    
    data_cursor = collection.find({})
    data_list = list(data_cursor)
    
    # convert list  into dataframe
    df = pd.DataFrame(data_list)
    
    # Convert the timestamp field to proper datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # creating new column to save the rounded timestamp
    df["rounded_timestamp"] = df["timestamp"].apply(lambda dt: round_to_nearest_interval(dt, interval_minutes=5))
    
    print("Data with sync timestamps (first five rows):\n",df[["timestamp","rounded_timestamp"]].head())
    
    # updating the data in the database
    for  index, row in df.iterrows():
        collection.update_one(
			{"_id":row["_id"]},
			{"$set":{"timestamp":row["rounded_timestamp"]}}
		)
        print("Updated document with id:", row["_id"])
        
    client.close()
    print("Database updated successfully...")
    
    
    
    
    
__name__ == "__main__"
main()