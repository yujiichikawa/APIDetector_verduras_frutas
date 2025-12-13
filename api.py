from datetime import datetime

from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
from PIL import Image
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['Caixa']
catalog_collection = db['catalog']
orders_collection = db['orders']

app = Flask(__name__)

model = YOLO('/home/thiago/Documentos/APIDetector_verduras_frutas/peso/best.pt')

cart = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400


    image_file = request.files['image']
    img = Image.open(image_file.stream)

    results = model.predict(img)
    detections = results[0].boxes.data.cpu().numpy()

    for detection in detections:
        class_id = int(detection[5])
        class_name = model.names[class_id]
        print(model.names)
        product = catalog_collection.find_one({'name': class_name})
        if product:
            existing_product = next((item for item in cart if item['name'] == class_name), None)
            if existing_product:
                existing_product['quantity'] += 1
                existing_product['total_price'] += product['price_per_kg']
            else:
                cart.append({
                    'name': product.get('display_name', class_name),
                    'price_per_kg': product['price_per_kg'],
                    'weight': 1.0,
                    'quantity': 1,
                    'total_price': product['price_per_kg'] * 1.0
                })

    return jsonify({'cart': cart})


@app.route('/remove', methods=['POST'])
def remove_item():
    data = request.get_json()
    product_name = data.get('name')

    global cart
    cart = [item for item in cart if item['name'] != product_name]

    return jsonify({'cart': cart})


@app.route('/clear', methods=['POST'])
def clear_cart():
    global cart
    cart = []
    return jsonify({'cart': cart})


@app.route('/cart', methods=['GET'])
def get_cart():
    return jsonify({'cart': cart})

@app.route('/catalog/search', methods=['GET'])
def search_catalog():
    name_query = request.args.get('name', '').lower()
    min_price = request.args.get('min_price', type=float, default=0.0)
    max_price = request.args.get('max_price', type=float, default=float('inf'))

    query = {
        'price_per_kg': {'$gte': min_price, '$lte': max_price}
    }

    if name_query:
        query['name'] = {'$regex': name_query, '$options': 'i'}

    results = list(catalog_collection.find(query, {'_id': 0}))
    return jsonify({'results': results})

@app.route('/checkout', methods=['POST'])
def checkout():
    global cart
    if not cart:
        return jsonify({'error': 'Carrinho vazio'}), 400

    order = {
        'items': cart,
        'total': sum(item['total_price'] for item in cart),
        'date': datetime.now()
    }
    orders_collection.insert_one(order)
    cart = []
    return jsonify({'message': 'Compra finalizada com sucesso!'})


@app.route('/orders', methods=['GET'])
def get_orders():
    orders = list(orders_collection.find({}, {'_id': 0}))
    return jsonify({'orders': orders})

if __name__ == '__main__':
    app.run(debug=True)
