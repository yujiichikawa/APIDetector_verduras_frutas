from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
from PIL import Image

app = Flask(__name__)

model = YOLO('C:/Users/user\PycharmProjects/APIDetector_verduras_frutas/peso/best.pt')

cart = []

catalog = {
    'onion': {'price_per_kg': 3.0},
    'potato':{'price_per_kg': 5.0}
}

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
        if class_name in catalog:
            existing_product = next((item for item in cart if item['name'] == class_name), None)
            if existing_product:
                existing_product['quantity'] += 1
                existing_product['total_price'] += catalog[class_name]['price_per_kg']
            else:
                product = {
                    'name': class_name,
                    'price_per_kg': catalog[class_name]['price_per_kg'],
                    'weight': 1.0,  # Peso fixo em 1kg
                    'quantity': 1,
                    'total_price': catalog[class_name]['price_per_kg'] * 1.0
                }
                cart.append(product)

    return jsonify({'cart': cart})


@app.route('/remove', methods=['POST'])
def remove_item():
    data = request.get_json()
    product_name = data.get('name')

    global cart
    cart = [item for item in cart if item['name'] != product_name]

    return jsonify({'cart': cart})


@app.route('/cart', methods=['GET'])
def get_cart():
    return jsonify({'cart': cart})


if __name__ == '__main__':
    app.run(debug=True)
