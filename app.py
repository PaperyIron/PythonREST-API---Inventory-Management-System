from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "025293600577",
        "quantity": 10,
        "price": 3.99,
        "category": "Beverages"
    },
    {
        "id": 2,
        "product_name": "Whole Grain Bread",
        "brands": "Bread",
        "barcode": "013093502006",
        "quantity": 5,
        "price": 5.49,
        "category": "Bakery"
    },
    {
        "id": 3,
        "product_name": "Greek Yogurt",
        "brands": "Chobani",
        "barcode": "894700010045",
        "quantity": 20,
        "price": 1.29,
        "category": "Dairy"
    },
    {
        "id": 4,
        "product_name": "Organic Peanut Butter",
        "brands": "Teddie",
        "barcode": "070462003918",
        "quantity": 8,
        "price": 7.99,
        "category": "Spreads"
    },
    {
        "id": 5,
        "product_name": "Apple Juice",
        "brands": "Martinelli's",
        "barcode": "041508706012",
        "quantity": 15,
        "price": 4.99,
        "category": "Beverages"
    }
]

next_id = 6

def find_item_id(id):
    for item in inventory:
        if item['id'] == id:
            return item
    return None

def fetch_openfoodfacts_data(barcode):
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data.get('status') == 1:
                product = data.get('product', {})
                return {
                    "product_name": product.get('product_name', 'Unknown'),
                    "brands": product.get('brands', 'Unknown'),
                    "barcode": barcode,
                    "category": product.get('categories', 'Uncategorized'),
                }
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OpenFoodFacts: {e}")
        return None
    
@app.route('/')
def home():
    return jsonify({
        "message": "Food Inventory Management API",
        "endpoints": {
            "GET /inventory": "Fetch all inventory items",
            "GET /inventory/<id>": "Fetch a specific item",
            "POST /inventory": "Add a new item",
            "PATCH /inventory/<id>": "Update an existing item",
            "DELETE /inventory/<id>": "Delete an item",
            "GET /openfoodfacts/<barcode>": "Fetch product from OpenFoodFacts"
        }
    })


@app.route('/inventory', methods=['GET'])
def get_all_inventory():
    return jsonify(inventory), 200


@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    item = find_item_id(item_id)
    
    if item:
        return jsonify(item), 200
    else:
        return jsonify({"error": "Item not found"}), 404


@app.route('/inventory', methods=['POST'])
def add_inventory_item():
    global next_id
    
    # Get JSON data from request
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['product_name', 'quantity', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create new item
    new_item = {
        "id": next_id,
        "product_name": data.get('product_name'),
        "brands": data.get('brands', 'Unknown'),
        "barcode": data.get('barcode', ''),
        "quantity": data.get('quantity'),
        "price": data.get('price'),
        "category": data.get('category', 'Uncategorized')
    }
    
    # Add to inventory
    inventory.append(new_item)
    next_id += 1
    
    return jsonify(new_item), 201


@app.route('/inventory/<int:item_id>', methods=['PATCH'])
def update_inventory_item(item_id):
    item = find_item_id(item_id)
    
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    # Get update data
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update allowed fields
    allowed_fields = ['product_name', 'brands', 'barcode', 'quantity', 'price', 'category']
    
    for field in allowed_fields:
        if field in data:
            item[field] = data[field]
    
    return jsonify(item), 200


@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    global inventory
    
    item = find_item_id(item_id)
    
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    # Remove item from inventory
    inventory = [i for i in inventory if i['id'] != item_id]
    
    return jsonify({"message": f"Item {item_id} deleted successfully"}), 200


@app.route('/openfoodfacts/<barcode>', methods=['GET'])
def get_openfoodfacts_product(barcode):
    product_data = fetch_openfoodfacts_data(barcode)
    
    if product_data:
        return jsonify(product_data), 200
    else:
        return jsonify({"error": "Product not found in OpenFoodFacts database"}), 404
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)