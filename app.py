from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import random

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb+srv://rankit2883:rankit2883@jobportal.vrbvj8m.mongodb.net/')
db = client['data_collection']
collection = db['entries']

@app.route("/")
def home():
    return render_template("index.html")

def convert_value_to_number(value):
    """Convert dropdown value to actual number"""
    mapping = { 
        '10': 10,
        '100': 100,
        '1k': 1000,
        '5k': 5000,
        '10k': 10000,
        '100k': 100000
    }
    return mapping.get(value, 0)

def generate_sample_data(count):
    """Generate sample data rows"""
    data = []
    for i in range(count):
        entry = {
            'id': i + 1,
            'name': f'User_{i+1}',
            'email': f'user{i+1}@example.com',
            'value': random.randint(100, 1000),
            'timestamp': datetime.now(),
            'status': random.choice(['Active', 'Inactive', 'Pending'])
        }
        data.append(entry)
    return data

@app.route("/submit", methods=["POST", "GET"])
def submit():
    if request.method == "POST":
        data_range = request.form.get("data_range")
        page = 1
    else:
        data_range = request.args.get("data_range")
        page = int(request.args.get("page", 1))
    
    if data_range:
        num_rows = convert_value_to_number(data_range)
        
        # Clear previous data from collection (only on POST)
        if request.method == "POST":
            collection.delete_many({})
            # Generate and insert sample data
            sample_data = generate_sample_data(num_rows)
            collection.insert_many(sample_data)
        
        # Pagination settings
        rows_per_page = 10
        skip = (page - 1) * rows_per_page
        
        # Fetch paginated data
        total_rows = collection.count_documents({})
        inserted_data = list(collection.find({}, {'_id': 0}).skip(skip).limit(rows_per_page))
        
        # Calculate pagination info
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        
        return render_template(
            "index.html", 
            selected_value=data_range,
            num_rows=total_rows,
            table_data=inserted_data,
            current_page=page,
            total_pages=total_pages
        )
    return redirect(url_for("home"))
 
if __name__ == "__main__":
    app.run(debug=True)