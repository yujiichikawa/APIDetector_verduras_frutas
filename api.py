from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
from PIL import Image
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://ythiago0000:6aLcl2e4XD0F2Bxo@cluster0.ibuk7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['Caixa']
catalog_collection = db['catalog']

app = Flask(__name__)

model = YOLO('C:/Users/user\PycharmProjects/APIDetector_verduras_frutas/peso/best.pt')

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
        product = catalog_collection.find_one({'name': class_name})
        if product:
            existing_product = next((item for item in cart if item['name'] == class_name), None)
            if existing_product:
                existing_product['quantity'] += 1
                existing_product['total_price'] += product['price_per_kg']
            else:
                cart.append({
                    'name': class_name,
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


if __name__ == '__main__':
    app.run(debug=True)
