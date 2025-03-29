import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def fetch_data():
    """
    Connect to MongoDB and fetch sensor data as a pandas DataFrame.
    """
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas"]
    
    # Fetch all documents
    data_cursor = collection.find({})
    data_list = list(data_cursor)
    client.close()
    
    # Convert to DataFrame
    return pd.DataFrame(data_list)

def determine_optimal_k(scaled_features, max_k=10):
    """
    Compute the Within-Cluster Sum of Squares (WCSS) for k values from 1 to max_k.
    This helps in determining the optimal number of clusters using the Elbow method.
    """
    wcss = []
    for k in range(1, max_k+1):
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(scaled_features)
        wcss.append(kmeans.inertia_)
    
    # Plot the elbow curve for visual inspection (optional)
    plt.plot(range(1, max_k+1), wcss, marker='o')
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("WCSS")
    plt.title("Elbow Method For Optimal k")
    plt.show()
    
    return wcss

def cluster_data(scaled_features, k):
    """
    Fit the K-Means model with k clusters and return the cluster labels.
    """
    kmeans = KMeans(n_clusters=k, random_state=0)
    clusters = kmeans.fit_predict(scaled_features)
    return clusters

def update_database(df):
    """
    Update only the 'cluster' field in each MongoDB document if it's not already labeled.
    """
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas"]
    
    updated_count = 0
    
    for index, row in df.iterrows():
        # Check if the document already has a cluster value (0,1,2)
        existing_doc = collection.find_one({"_id": row["_id"]}, {"cluster": 1})
        
        if existing_doc and "cluster" in existing_doc and existing_doc["cluster"] in [0, 1, 2]:
            print(f"Skipping update for document ID: {row['_id']} (cluster already exists: {existing_doc['cluster']})")
            continue  # Skip updating this document

        # Otherwise, update the cluster field
        result = collection.update_one(
            {"_id": row["_id"]},  # Find the document by _id
            {"$set": {"cluster": int(row["cluster"])}}  # Only update "cluster"
        )
        
        if result.modified_count > 0:
            updated_count += 1
            print(f"Updated document ID: {row['_id']} with cluster: {row['cluster']}")

    print(f"Total documents updated: {updated_count}")
    client.close()

def main():
    # Step 1: Fetch data from MongoDB
    df = fetch_data()
    print("Fetched data (first 5 rows):\n", df.head())

    # Step 2: Preprocess Data - select features and normalize
    features = df[['temperature', 'humidity', 'mq135']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Step 3: (Optional) Use the Elbow Method to determine optimal k
    print("Calculating WCSS for different k values...")
    determine_optimal_k(scaled_features, max_k=10)
    
    # Fixed k value (chosen manually)
    optimal_k = 3
    print("Optimal k chosen:", optimal_k)

    # Step 4: Cluster Data using K-Means and assign cluster labels to a new 'cluster' column
    df['cluster'] = cluster_data(scaled_features, optimal_k)
    print("Data with cluster labels (first 5 rows):\n", df.head())

    # Step 5: Keep only required columns (_id and cluster) before updating MongoDB
    df = df[["_id", "cluster"]]

    # Step 6: Update MongoDB with only the cluster field (skip existing cluster values)
    print("Updating database with cluster labels...")
    update_database(df)
    print("Database has been updated with cluster labels.")

if __name__ == '__main__':
    main()
