# main.py
import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def fetch_data():
    """
    Connect to MongoDB and fetch sensor data as a pandas DataFrame.
    """
    # Replace with your MongoDB connection string, database and collection names.
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas"]
    # Fetch all documents; adjust query if needed
    data_cursor = collection.find({})
    data_list = list(data_cursor)
    client.close()
    # Convert to DataFrame; ensure _id remains so you can update documents later.
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
    Update each MongoDB document with its corresponding cluster label.
    The DataFrame must contain a column '_id' for matching documents.
    """
    # Replace with your connection string, database and collection names.
    client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")
    db = client["plantree"]
    collection = db["sensordatas"]
    for index, row in df.iterrows():
        # Update document by _id with the new 'cluster' field
        collection.update_one(
            {"_id": row["_id"]},
            {"$set": {"label": int(row["cluster"])}}
        )
    client.close()

def main():
    # Step 1: Fetch data from MongoDB
    df = fetch_data()
    print("Fetched data (first 5 rows):\n", df.head())

    # Step 2: Preprocess Data - select features and normalize them.
    # Here we use temperature, humidity, and mq135 as features.
    features = df[['temperature', 'humidity', 'mq135']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Step 3: (Optional) Use the Elbow Method to determine optimal k.
    # This will plot a graph. For a production system, you may choose a fixed k.
    print("Calculating WCSS for different k values...")
    wcss = determine_optimal_k(scaled_features, max_k=10)
    # For example, suppose we decide k = 3 based on the elbow plot.
    optimal_k = 3
    print("Optimal k chosen:", optimal_k)

    # Step 4: Cluster Data using K-Means with optimal k.
    df['cluster'] = cluster_data(scaled_features, optimal_k)
    print("Data with cluster labels (first 5 rows):\n", df.head())

    # Step 5: Update the MongoDB database with the new cluster labels.
    print("Updating database with cluster labels...")
    update_database(df)
    print("Database has been updated with cluster labels.")

if __name__ == '__main__':
    main()
