import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def fetch_unlabeled_data():
    """
    Fetch only unlabeled data (where 'cluster' field does not exist).
    """
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas"]
    
    # Only fetch documents where 'cluster' field is missing
    data_cursor = collection.find({"cluster": {"$exists": False}})
    data_list = list(data_cursor)
    client.close()
    
    return pd.DataFrame(data_list)

def cluster_data(df, k=3):
    """
    Apply KMeans clustering to given DataFrame.
    """
    features = df[['temperature', 'humidity', 'mq135']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=k, random_state=0, n_init='auto')
    df['cluster'] = kmeans.fit_predict(scaled_features)
    
    return df[['_id', 'cluster']]

def update_clusters(df):
    """
    Update cluster labels in MongoDB for unlabeled records.
    """
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas"]
    
    updated_count = 0
    for _, row in df.iterrows():
        result = collection.update_one(
            {"_id": row["_id"]},
            {"$set": {"cluster": int(row["cluster"])}}
        )
        print(f"Updated document with _id: {row['_id']} to cluster: {row['cluster']}")
        if result.modified_count > 0:
            updated_count += 1

    client.close()
    print(f"✅ Updated {updated_count} new documents.")

def main():
    print("🔄 Fetching only unlabeled documents...")
    df = fetch_unlabeled_data()

    if df.empty:
        print("✅ No unlabeled data found. Nothing to update.")
        return

    print(f"📦 Fetched {len(df)} unlabeled documents.")
    df = cluster_data(df, k=3)
    
    print("📤 Updating MongoDB with new cluster labels...")
    update_clusters(df)

if __name__ == "__main__":
    main()
