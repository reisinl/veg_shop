"""
@file
@brief This module defines the database models for the Vegetable Shop application using SQLAlchemy.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
from app import create_app

app = create_app()

db = SQLAlchemy(app)

class Person(db.Model):
    """
    @brief Base model representing a person.
    @details This class defines the common attributes for all person entities in the system.
    """
    __tablename__ = 'persons'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)

class Staff(Person):
    """
    @brief Model representing a staff member.
    @details Extends the Person model with staff-specific attributes and relationships.
    """
    __tablename__ = 'staff'

    id = db.Column(db.Integer, db.ForeignKey('persons.id'), primary_key=True)
    date_joined = db.Column(db.Date, default=datetime.now)
    dept_name = db.Column(db.String(100), nullable=False)
    staff_id = db.Column(db.String(100), unique=True, nullable=False)

    list_of_customers = db.relationship('Customer', backref='staff', lazy=True)
    list_of_orders = db.relationship('Order', backref='staff', lazy=True, foreign_keys='Order.staff_id')
    premade_boxes = db.relationship('PremadeBox', backref='staff', lazy=True, foreign_keys='PremadeBox.staff_id')
    veggies = db.relationship('Veggie', backref='staff', lazy=True, foreign_keys='Veggie.staff_id')

class Customer(Person):
    """
    @brief Model representing a customer.
    @details Extends the Person model with customer-specific attributes and relationships.
    """
    __tablename__ = 'customers'

    id = db.Column(db.Integer, db.ForeignKey('persons.id'), primary_key=True)
    cust_address = db.Column(db.String(255), nullable=False)
    cust_balance = db.Column(db.Float, default=0.0)
    cust_id = db.Column(db.String(100), unique=True, nullable=False)
    max_owing = db.Column(db.Float, default=1000.0)
    distance_from_store = db.Column(db.Float, nullable=False)

    list_of_orders = db.relationship('Order', backref='customer', lazy=True)
    list_of_payments = db.relationship('Payment', backref='customer', lazy=True)

class CorporateCustomer(Customer):
    """
    @brief Model representing a corporate customer.
    @details Extends the Customer model with corporate-specific attributes.
    """
    __tablename__ = 'corporate_customers'

    id = db.Column(db.Integer, db.ForeignKey('customers.id'), primary_key=True)
    discount_rate = db.Column(db.Float, default=0.05)
    max_credit = db.Column(db.Float, default=10000.0)
    min_balance = db.Column(db.Float, default=1000.0)
    distance_from_store = db.Column(db.Float, nullable=False)
    

class Item(db.Model):
    """
    @brief Base model representing an item.
    @details Defines common attributes for all items in the inventory.
    """
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    type = db.Column(db.String(50))
    stock_quantity = db.Column(db.Integer)

class Veggie(Item):
    """
    @brief Model representing a vegetable item.
    @details Extends the Item model with vegetable-specific attributes.
    """
    __tablename__ = 'veggies'

    id = db.Column(db.Integer, db.ForeignKey('items.id'), primary_key=True)
    veg_name = db.Column(db.String(100), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

class WeightedVeggie(Veggie):
    """
    @brief Model representing a weighted vegetable item.
    @details Extends the Veggie model with weight-specific attributes.
    """
    __tablename__ = 'weighted_veggies'

    id = db.Column(db.Integer, db.ForeignKey('veggies.id'), primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    weight_per_kilo = db.Column(db.Float, nullable=False)

class PackVeggie(Veggie):
    """
    @brief Model representing a packaged vegetable item.
    @details Extends the Veggie model with package-specific attributes.
    """
    __tablename__ = 'pack_veggies'

    id = db.Column(db.Integer, db.ForeignKey('veggies.id'), primary_key=True)
    num_of_pack = db.Column(db.Integer, nullable=False)
    price_per_pack = db.Column(db.Float, nullable=False)

class UnitPriceVeggie(Veggie):
    """
    @brief Model representing a vegetable sold by unit price.
    @details Extends the Veggie model with unit-specific attributes.
    """
    __tablename__ = 'unit_price_veggies'

    id = db.Column(db.Integer, db.ForeignKey('veggies.id'), primary_key=True)
    price_per_unit = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class PremadeBox(Item):
    """
    @brief Model representing a premade box item.
    @details Extends the Item model with box-specific attributes and methods.
    """
    __tablename__ = 'premade_boxes'

    id = db.Column(db.Integer, db.ForeignKey('items.id'), primary_key=True)
    box_size = db.Column(db.String(50), nullable=False)  # 'Small', 'Medium', 'Large'
    num_of_boxes = db.Column(db.Integer, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

    def box_price(self):
        """
        @brief Calculate the price of the box based on its size and quantity.
        @return Total price of the premade boxes.
        """
        base_price = 10.0  # Base price
        price_multiplier = 1.0

        if self.box_size == 'Small':
            price_multiplier = 1.0
        elif self.box_size == 'Medium':
            price_multiplier = 1.5
        elif self.box_size == 'Large':
            price_multiplier = 2.0

        return base_price * price_multiplier * self.num_of_boxes

class Order(db.Model):
    """
    @brief Model representing an order.
    @details Defines attributes and relationships for customer orders.
    """
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_customer = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    order_date = db.Column(db.DateTime, default=datetime.now)
    order_number = db.Column(db.String(100), unique=True, nullable=False)
    order_status = db.Column(db.String(50), nullable=False)  # 'Pending', 'Completed', etc.
    total_amount = db.Column(db.Float, nullable=False)

    order_lines = db.relationship('OrderLine', backref='order', lazy=True)
    payments = db.relationship('Payment', backref='order', lazy=True)

class OrderLine(db.Model):
    """
    @brief Model representing an order line.
    @details Each order line corresponds to an item and its quantity in an order.
    """
    __tablename__ = 'order_lines'

    id = db.Column(db.Integer, primary_key=True)
    item_number = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_type = db.Column(db.String(50))

    item = db.relationship('Item', backref='order_lines')

class Payment(db.Model):
    """
    @brief Model representing a payment.
    @details Defines attributes and relationships for payments made by customers.
    """
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    payment_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_id = db.Column(db.String(100), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

class CreditCardPayment(Payment):
    """
    @brief Model representing a credit card payment.
    @details Extends the Payment model with credit card-specific attributes.
    """
    __tablename__ = 'credit_card_payments'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    card_expiry_date = db.Column(db.String(5), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    card_type = db.Column(db.String(50), nullable=False)

class DebitCardPayment(Payment):
    """
    @brief Model representing a debit card payment.
    @details Extends the Payment model with debit card-specific attributes.
    """
    __tablename__ = 'debit_card_payments'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    bank_name = db.Column(db.String(100), nullable=False)
    debit_card_number = db.Column(db.String(16), nullable=False)
