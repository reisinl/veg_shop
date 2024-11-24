CREATE DATABASE IF NOT EXISTS vegetable_shop;
USE vegetable_shop;

-- Drop existing tables in a dependent order to avoid constraint issues

DROP TABLE IF EXISTS corporate_customers;
DROP TABLE IF EXISTS weighted_veggies;
DROP TABLE IF EXISTS pack_veggies;
DROP TABLE IF EXISTS unit_price_veggies;
DROP TABLE IF EXISTS veggies;
DROP TABLE IF EXISTS premade_boxes;

DROP TABLE IF EXISTS credit_card_payments;
DROP TABLE IF EXISTS debit_card_payments;

DROP TABLE IF EXISTS order_lines;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS persons;


USE vegetable_shop;

-- Create tables as per the updated model structure
CREATE TABLE persons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE customers (
    id INT PRIMARY KEY,
    cust_id VARCHAR(100) UNIQUE NOT NULL,
    cust_address VARCHAR(255) NOT NULL,
    cust_balance FLOAT DEFAULT 0.0,
    max_owing FLOAT DEFAULT 1000.0,
    distance_from_store FLOAT NOT NULL,
    FOREIGN KEY (id) REFERENCES persons(id)
);

CREATE TABLE corporate_customers (
    id INT PRIMARY KEY,
    discount_rate FLOAT DEFAULT 0.05,
    max_credit FLOAT DEFAULT 10000.0,
    min_balance FLOAT DEFAULT 1000.0,
    distance_from_store FLOAT NOT NULL,
    FOREIGN KEY (id) REFERENCES customers(id)
);

CREATE TABLE staff (
    id INT PRIMARY KEY,
    date_joined DATE DEFAULT (curdate()),
    dept_name VARCHAR(100) NOT NULL,
    staff_id VARCHAR(100) UNIQUE NOT NULL,
    FOREIGN KEY (id) REFERENCES persons(id)
);

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    price FLOAT NOT NULL CHECK (price >= 0.0),
    type VARCHAR(50),
    stock_quantity INT DEFAULT 0 CHECK (stock_quantity >= 0)
);

CREATE TABLE veggies (
    id INT PRIMARY KEY,
    veg_name VARCHAR(100) NOT NULL,
    staff_id INT,
    FOREIGN KEY (id) REFERENCES items(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE TABLE weighted_veggies (
    id INT PRIMARY KEY,
    weight FLOAT NOT NULL,
    weight_per_kilo FLOAT NOT NULL,
    FOREIGN KEY (id) REFERENCES veggies(id)
);

CREATE TABLE pack_veggies (
    id INT PRIMARY KEY,
    num_of_pack INT NOT NULL,
    price_per_pack FLOAT NOT NULL,
    FOREIGN KEY (id) REFERENCES veggies(id)
);

CREATE TABLE unit_price_veggies (
    id INT PRIMARY KEY,
    price_per_unit FLOAT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (id) REFERENCES veggies(id)
);

CREATE TABLE premade_boxes (
    id INT PRIMARY KEY,
    box_size VARCHAR(50) NOT NULL,
    num_of_boxes INT NOT NULL,
    staff_id INT,
    FOREIGN KEY (id) REFERENCES items(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    total_amount FLOAT NOT NULL,  -- Added to store the total amount of the order
    order_customer INT NOT NULL,
    staff_id INT,
    FOREIGN KEY (order_customer) REFERENCES customers(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE TABLE order_lines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_number INT NOT NULL,
    order_id INT NOT NULL,
    quantity INT DEFAULT 1,
    order_type VARCHAR(50),
    FOREIGN KEY (item_number) REFERENCES items(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_amount FLOAT NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50) NOT NULL,
    customer_id INT NOT NULL,
    payment_id VARCHAR(100) UNIQUE NOT NULL,
    order_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);


CREATE TABLE credit_card_payments (
    id INT PRIMARY KEY,
    card_expiry_date VARCHAR(5) NOT NULL,
    card_number VARCHAR(16) NOT NULL,
    card_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (id) REFERENCES payments(id)
);

CREATE TABLE debit_card_payments (
    id INT PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    debit_card_number VARCHAR(16) NOT NULL,
    FOREIGN KEY (id) REFERENCES payments(id)
);

-- Insert sample persons (users)
INSERT INTO persons (first_name, last_name, password, username)
VALUES 
('John', 'Doe', '123', '111'),
('Jane', 'Smith', '123', '222'),
('Alice', 'Brown', '123', '333'),
('Tom', 'Smith', '123', '444'),
('Doe', 'Brown', '123', '555'),
('Corp', 'Cust', '123', '666');

-- Insert sample customers
INSERT INTO customers (id, cust_id, cust_address, cust_balance, max_owing, distance_from_store)
VALUES 
(1, 1, '123 Apple St Auckland', 100.0, 100, 19),
(2, 2, '456 Banana Ave Wellington', 50.0, 80.0, 20),
(3, 3, '789 Banana Ave Wellington', 40.0, 10.0, 21),
(6, 6, '700 Mango Ave Christchurch', 1200.0, 10.0, 19);


-- Insert sample staff
INSERT INTO staff (id, date_joined, dept_name, staff_id)
VALUES 
(3, '2024-01-15', 'Sales', 'STAFF001'),
(4, '2024-02-20', 'Admin', 'STAFF002'),
(5, '2024-03-01', 'Marketing', 'STAFF003');

-- Insert sample corp customer
INSERT INTO corporate_customers values (6,10,100,1000,19);

-- Insert sample items (added description column)
INSERT INTO items (name, price, type, stock_quantity, description)
VALUES 
('Carrot', 2.5, 'Veggie', 100, 'Fresh organic carrots'),
('Broccoli', 3.0, 'Veggie', 150, 'Green and healthy broccoli'),
('Onion', 2.5, 'Veggie', 100, 'Fresh organic Onion'),
('Spring Onion', 3.0, 'Veggie', 150, 'Green and healthy spring onion'),
('Leek', 2.5, 'Veggie', 100, 'Fresh organic leek'),
('Avacado', 3.0, 'Veggie', 150, 'Green and healthy Avacado'),
('Premade Box - Small', 10.0, 'Box', 20, 'A small box with assorted veggies'),
('Premade Box - Medium', 15.0, 'Box', 10, 'A medium box with more assorted veggies'),
('Premade Box - Large', 20.0, 'Box', 10, 'A medium box with more assorted veggies');

INSERT INTO items (name, description, price, type, stock_quantity) VALUES ('Unit Veggies', 'Veggies by unit', '0', 'Unit', '0');
INSERT INTO items (name, description, price, type, stock_quantity) VALUES ('Weight Veggies', 'Veggies by weight', '0', 'Weight', '0');
INSERT INTO items (name, description, price, type, stock_quantity) VALUES ('Pack Veggies', 'Veggies by Pack', '0', 'Pack', '0');


-- Insert sample veggies
INSERT INTO veggies (id, veg_name, staff_id)
VALUES
(1, 'Carrot', 3),
(2, 'Broccoli', 3),
(3, 'Onion', 3),
(4, 'Spring Onion', 3),
(5, 'Leek', 3),
(6, 'Avacado', 3);

-- Insert sample premade boxes
INSERT INTO premade_boxes (id, box_size, num_of_boxes, staff_id)
VALUES
(7, 'Small', 20, 3),
(8, 'Medium', 10, 3),
(9, 'Large', 10, 3);


INSERT INTO unit_price_veggies (id, price_per_unit, quantity) VALUES ('1', '5', '5');
INSERT INTO unit_price_veggies (id, price_per_unit, quantity) VALUES ('2', '10', '5');
INSERT INTO unit_price_veggies (id, price_per_unit, quantity) VALUES ('3', '5', '5');
INSERT INTO unit_price_veggies (id, price_per_unit, quantity) VALUES ('4', '10', '5');
INSERT INTO unit_price_veggies (id, price_per_unit, quantity) VALUES ('5', '5', '5');
INSERT INTO unit_price_veggies (id, price_per_unit, quantity) VALUES ('6', '10', '5');

INSERT INTO weighted_veggies (id, weight, weight_per_kilo) VALUES ('1', '1', '5');
INSERT INTO weighted_veggies (id, weight,weight_per_kilo) VALUES ('2', '1', 10);
INSERT INTO weighted_veggies (id, weight, weight_per_kilo) VALUES ('3', '1', '5');
INSERT INTO weighted_veggies (id, weight,weight_per_kilo) VALUES ('4', '1', 10);
INSERT INTO weighted_veggies (id, weight, weight_per_kilo) VALUES ('5', '1', '5');
INSERT INTO weighted_veggies (id, weight,weight_per_kilo) VALUES ('6', '1', 10);

INSERT INTO pack_veggies (id, num_of_pack, price_per_pack) VALUES ('1', '5', '5');
INSERT INTO pack_veggies (id, num_of_pack, price_per_pack) VALUES ('2', '5', '10');
INSERT INTO pack_veggies (id, num_of_pack, price_per_pack) VALUES ('3', '5', '5');
INSERT INTO pack_veggies (id, num_of_pack, price_per_pack) VALUES ('4', '5', '10');
INSERT INTO pack_veggies (id, num_of_pack, price_per_pack) VALUES ('5', '5', '5');
INSERT INTO pack_veggies (id, num_of_pack, price_per_pack) VALUES ('6', '5', '10');


