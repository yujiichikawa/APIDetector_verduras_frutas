from datetime import datetime
import os

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from ultralytics import YOLO
from PIL import Image

app = Flask(__name__)


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Catalog(db.Model):
    __tablename__ = "catalog"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    price_per_kg = db.Column(db.Float, nullable=False)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(50), nullable=False)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)


with app.app_context():
    db.create_all()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "peso", "best.pt")

model = YOLO(MODEL_PATH)

cart = []

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    image_file = request.files["image"]
    img = Image.open(image_file.stream)

    results = model.predict(img)
    detections = results[0].boxes.data.cpu().numpy()

    for detection in detections:
        class_id = int(detection[5])
        class_name = model.names[class_id]

        product = Catalog.query.filter_by(name=class_name).first()
        if not product:
            continue

        existing_product = next(
            (item for item in cart if item["name"] == product.display_name), None
        )

        if existing_product:
            existing_product["quantity"] += 1
            existing_product["total_price"] += product.price_per_kg
        else:
            cart.append({
                "name": product.display_name or product.name,
                "price_per_kg": product.price_per_kg,
                "weight": 1.0,
                "quantity": 1,
                "total_price": product.price_per_kg
            })

    return jsonify({"cart": cart})


@app.route("/catalog/search", methods=["GET"])
def search_catalog():
    name = request.args.get("name", "")
    min_price = request.args.get("min_price", type=float, default=0)
    max_price = request.args.get("max_price", type=float, default=9999)

    query = Catalog.query

    if name:
        query = query.filter(Catalog.name.ilike(f"%{name}%"))

    query = query.filter(Catalog.price_per_kg.between(min_price, max_price))

    results = [
        {
            "name": p.display_name or p.name,
            "price_per_kg": p.price_per_kg
        }
        for p in query.all()
    ]

    return jsonify({"results": results})


@app.route('/remove', methods=['POST'])
def remove_item():
    data = request.get_json()
    product_name = data.get('name', '').lower()

    global cart
    cart = [
        item for item in cart
        if item['name'].lower() != product_name
    ]

    return jsonify({'cart': cart})


@app.route("/clear", methods=["POST"])
def clear_cart():
    global cart
    cart = []
    return jsonify({"cart": cart})


@app.route("/cart", methods=["GET"])
def get_cart():
    return jsonify({"cart": cart})


@app.route("/checkout", methods=["POST"])
def checkout():
    global cart

    if not cart:
        return jsonify({"error": "Carrinho vazio"}), 400

    order = Order(
        total=sum(item["total_price"] for item in cart),
        date=datetime.now().isoformat()
    )
    db.session.add(order)
    db.session.commit()

    for item in cart:
        db.session.add(OrderItem(
            order_id=order.id,
            name=item["name"],
            quantity=item["quantity"],
            total_price=item["total_price"]
        ))

    db.session.commit()
    cart = []

    return jsonify({"message": "Compra finalizada com sucesso!"})


@app.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()

    response = []
    for order in orders:
        items = OrderItem.query.filter_by(order_id=order.id).all()
        response.append({
            "date": order.date,
            "total": order.total,
            "items": [
                {
                    "name": i.name,
                    "quantity": i.quantity,
                    "total_price": i.total_price
                } for i in items
            ]
        })

    return jsonify({"orders": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
