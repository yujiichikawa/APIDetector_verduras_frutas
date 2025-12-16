
CREATE TABLE IF NOT EXISTS catalog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    price_per_kg FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total FLOAT NOT NULL,
    date VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    name VARCHAR(100),
    quantity INT,
    total_price FLOAT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

INSERT INTO catalog (name, display_name, price_per_kg) VALUES
('banana', 'Banana', 4.50),
('apple', 'Maçã', 6.00),
('tomato', 'Tomate', 5.20),
('potato', 'Batata', 3.80),
('carrot', 'Cenoura', 4.10),
('onion', 'Cebola', 3.50);
