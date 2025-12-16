CREATE DATABASE IF NOT EXISTS hortvision;
USE hortvision;

CREATE TABLE IF NOT EXISTS catalog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    price_per_kg DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total DECIMAL(10,2),
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(100),
    quantity INT,
    total_price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

INSERT INTO catalog (name, display_name, price_per_kg) VALUES
('banana', 'Banana', 4.50),
('apple', 'Maçã', 6.00),
('tomato', 'Tomate', 5.20),
('potato', 'Batata', 3.80),
('carrot', 'Cenoura', 4.10),
('onion', 'Cebola', 3.50);

CREATE DATABASE IF NOT EXISTS zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

GRANT ALL PRIVILEGES ON zabbix.* TO 'hortuser'@'%';
FLUSH PRIVILEGES;