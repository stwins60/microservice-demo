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

with open('carts.json') as f:
    carts_data = json.load(f)

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

@app.route('/carts', methods=['GET'])
def get_carts():
    return jsonify(carts_data)

@app.route('/carts/<int:id>', methods=['GET'])
def get_cart(id):
    cart = next((cart for cart in carts_data['carts'] if cart['id'] == id), None)
    if cart:
        return jsonify(cart)
    return jsonify({'error': 'cart not found'}), 404

@app.route('/carts/user/<int:user_id>', methods=['GET'])
def get_user_cart(user_id):
    cart = next((cart for cart in carts_data['carts'] if cart['userId'] == user_id), None)
    if cart:
        return jsonify(cart)
    return jsonify({'error': 'cart not found'}), 404

@app.route('/carts', methods=['POST'])
def add_cart():
    cart = request.json
    carts_data.append(cart)
    return jsonify({'message': 'cart added successfully'}), 201

@app.route('/carts/<int:id>', methods=['PUT'])
def update_cart(id):
    cart = next((cart for cart in carts_data['carts'] if cart['id'] == id), None)
    if cart:
        cart.update(request.json)
        return jsonify({'message': 'cart updated successfully'})
    return jsonify({'error': 'cart not found'}), 404

@app.route('/carts/<int:id>', methods=['DELETE'])
def delete_cart(id):
    cart = next((cart for cart in carts_data['carts'] if cart['id'] == id), None)
    if cart:
        carts_data.remove(cart)
        return jsonify({'message': 'cart deleted successfully'})
    return jsonify({'error': 'cart not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)