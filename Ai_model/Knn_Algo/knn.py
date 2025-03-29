import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score

# Step 1: Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0")  # Replace with your MongoDB Atlas connection string
db = client['plantree']  # Replace with your database name
collection = db['sensordatas']  # Replace with your collection name



# Step 2: Fetch Data from MongoDB
cursor = collection.find()
data = list(cursor)  # Convert MongoDB cursor to a list

# Step 3: Load Data into Pandas DataFrame
df = pd.DataFrame(data)

print(df.head())  # This will print the first few rows of your dataset
print(df.columns)  # This will show all column names


# Step 4: Check if all required columns exist
required_columns = {'temperature', 'humidity', 'mq135', 'location', 'cluster'}
if not required_columns.issubset(df.columns):
    raise ValueError("Missing required columns in the dataset")

# Step 5: Create a target variable (1 = Needs Plantation, 0 = Doesn't Need Plantation)
df['needs_plantation'] = df['cluster'].apply(lambda x: 1 if x == 2 else 0)

# Step 6: Select Features and Labels
X = df[['temperature', 'humidity', 'mq135']]
y = df['needs_plantation']

# Step 7: Normalize Features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 8: Split Data for Training and Testing
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Step 9: Train KNN Model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

# Step 10: Evaluate the Model
y_pred = knn.predict(X_test)
print("KNN Test Accuracy:", accuracy_score(y_test, y_pred))

# Step 11: Predict on All Data
df['prediction'] = knn.predict(X_scaled)

# Step 12: Count Predictions Per Location
location_counts = df[df['prediction'] == 1]['location'].value_counts()

# Step 13: Identify the Area Needing the Most Trees
if not location_counts.empty:
    suggested_location = location_counts.idxmax()
    print("Suggested location for tree plantation:", suggested_location)
    print("Counts per location:")
    print(location_counts)
else:
    print("No areas require tree plantation based on KNN model predictions.")
    
precision = precision_score(y_test,y_pred)
recall = recall_score(y_test,y_pred)

print(f"KNN Test precision: {precision}")
print(f"KNN Test recall: {recall}")
