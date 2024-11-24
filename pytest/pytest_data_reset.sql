CREATE DATABASE IF NOT EXISTS vegetable_shop_test;
USE vegetable_shop_test;

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


USE vegetable_shop_test;

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
    order_id INT NOT NULL,  -- Added to associate the payment with a specific order
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)  -- Link payment to the specific order
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