from flask import  Flask, request, jsonify
from flask_cors import CORS
import secrets
import json

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
CORS(app)

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': '*',
    'SESSION_ID': app.secret_key
}

with open('products.json') as f:
    products = json.load(f)

@app.after_request
def add_headers(response):
    for key, value in headers.items():
        response.headers[key] = value
    return response

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = next((product for product in products['products'] if product['id'] == id), None)
    print(product)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

@app.route('/products/search/<string:query>', methods=['GET'])
def search_products(query):
    result = [product for product in products if query.lower() in product['name'].lower()]
    return jsonify(result)

@app.route('/products/category', methods=['GET'])
def get_categories():
    global products  # Make sure 'products' variable is accessible within the function
    categories = list(set([product['category'] for product in products['products']]))
    return jsonify(categories)

@app.route('/products/category/<string:category>', methods=['GET'])
def get_products_by_category(category):
    result = [product for product in products['products'] if category.lower() == product['category'].lower()]
    return jsonify(result)

@app.route('/products', methods=['POST'])
def add_product():
    product = request.json
    products.append(product)
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = next((product for product in products['products'] if product['id'] == id), None)
    if product:
        product.update(request.json)
        return jsonify({'message': 'Product updated successfully'})
    return jsonify({'error': 'Product not found'}), 404

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = next((product for product in products['products'] if product['id'] == id), None)
    if product:
        products.remove(product)
        return jsonify({'message': 'Product deleted successfully'})
    return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)