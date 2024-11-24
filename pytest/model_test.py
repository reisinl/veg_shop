# model_testls.py
import sys
import os

# Get the parent directory of the current file (model_test.py)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

import pytest
from datetime import datetime, timezone
from models import app, db 
from models import (
    Person, Staff, Customer, CorporateCustomer, Item, Veggie,
    WeightedVeggie, PackVeggie, UnitPriceVeggie, PremadeBox,
    Order, OrderLine, Payment, CreditCardPayment, DebitCardPayment
)
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

# --------------------------------------------
# Fixtures
# --------------------------------------------

@pytest.fixture(scope='module')
def test_client():
    """
    Pytest fixture to set up a Flask test client with a MySQL test database.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root2024@localhost/vegetable_shop_test'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    testing_client = app.test_client()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield testing_client
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function', autouse=True)
def session_scope():
    """
    Ensure each test runs in its own transaction,
    which is rolled back at the end of the test.
    """
    # Start a transaction
    connection = db.engine.connect()
    transaction = connection.begin()

    # Create a new session bound to the connection
    session_factory = sessionmaker(bind=connection)
    Session = scoped_session(session_factory)
    db.session = Session  # Override db.session

    yield

    transaction.rollback()
    connection.close()
    Session.remove()

@pytest.fixture
def staff_member():
    """
    Fixture to create a staff member.
    """
    staff = Staff(
        first_name='Alice',
        last_name='Smith',
        password='password123',
        username='alicesmith',
        date_joined=datetime.now(timezone.utc),
        dept_name='Sales',
        staff_id='S123'
    )
    db.session.add(staff)
    db.session.flush()
    return staff


@pytest.fixture
def customer():
    """
    Fixture to create a customer.
    """
    customer = Customer(
        first_name='Bob',
        last_name='Johnson',
        password='password123',
        username='bobjohnson',
        cust_address='123 Main St',
        cust_balance=100.0,
        cust_id='C123',
        max_owing=500.0,
        distance_from_store=10.0
    )
    db.session.add(customer)
    db.session.flush()  # Use flush instead of commit
    return customer


# --------------------------------------------
# Test Functions
# --------------------------------------------

def test_person_model(test_client):
    """
    Test the Person model for basic CRUD operations.
    """
    person = Person(
        first_name='John',
        last_name='Doe',
        password='password123',
        username='johndoe'
    )
    db.session.add(person)
    db.session.flush()

    retrieved_person = Person.query.filter_by(username='johndoe').first()
    assert retrieved_person is not None
    assert retrieved_person.first_name == 'John'
    assert retrieved_person.last_name == 'Doe'

def test_staff_model(test_client):
    """
    Test the Staff model and its relationship with Person.
    """
    staff = Staff(
        first_name='Alice',
        last_name='Smith',
        password='password123',
        username='alicesmith',
        date_joined=datetime.now(timezone.utc),
        dept_name='Sales',
        staff_id='S123'
    )
    db.session.add(staff)
    db.session.flush()

    retrieved_staff = Staff.query.filter_by(username='alicesmith').first()
    assert retrieved_staff is not None
    assert retrieved_staff.dept_name == 'Sales'
    assert retrieved_staff.staff_id == 'S123'

def test_customer_model(test_client):
    """
    Test the Customer model and its relationship with Person.
    """
    customer = Customer(
        first_name='Bob',
        last_name='Johnson',
        password='password123',
        username='bobjohnson',
        cust_address='123 Main St',
        cust_balance=100.0,
        cust_id='C123',
        max_owing=500.0,
        distance_from_store=10.0
    )
    db.session.add(customer)
    db.session.flush()

    retrieved_customer = Customer.query.filter_by(username='bobjohnson').first()
    assert retrieved_customer is not None
    assert retrieved_customer.cust_address == '123 Main St'
    assert retrieved_customer.cust_balance == 100.0

def test_corporate_customer_model(test_client):
    """
    Test the CorporateCustomer model and its inheritance from Customer.
    """
    corporate_customer = CorporateCustomer(
        first_name='Corp',
        last_name='Customer',
        password='password123',
        username='corpcustomer',
        cust_address='789 Corporate Ave',
        cust_balance=5000.0,
        cust_id='C789',
        max_owing=20000.0,
        distance_from_store=15.0,
        discount_rate=0.1,
        max_credit=50000.0,
        min_balance=5000.0
    )
    db.session.add(corporate_customer)
    db.session.flush()

    retrieved_corporate_customer = CorporateCustomer.query.filter_by(username='corpcustomer').first()
    assert retrieved_corporate_customer is not None
    assert retrieved_corporate_customer.discount_rate == 0.1

def test_item_model(test_client):
    """
    Test the Item model for basic CRUD operations.
    """
    item = Item(
        name='Carrot',
        description='Fresh carrots',
        price=2.5,
        type='Vegetable',
        stock_quantity=100
    )
    db.session.add(item)
    db.session.flush()

    retrieved_item = Item.query.filter_by(name='Carrot').first()
    assert retrieved_item is not None
    assert retrieved_item.price == 2.5
    assert retrieved_item.stock_quantity == 100

def test_veggie_model(test_client, staff_member):
    """
    Test the Veggie model and its inheritance from Item.
    """
    veggie = Veggie(
        name='Tomato',
        description='Organic tomatoes',
        price=3.0,
        type='Vegetable',
        stock_quantity=50,
        veg_name='Tomato',
        staff_id=staff_member.id
    )
    db.session.add(veggie)
    db.session.flush()

    retrieved_veggie = Veggie.query.filter_by(veg_name='Tomato').first()
    assert retrieved_veggie is not None
    assert retrieved_veggie.staff_id == staff_member.id

def test_weighted_veggie_model(test_client, staff_member):
    """
    Test the WeightedVeggie model and its inheritance from Veggie.
    """
    weighted_veggie = WeightedVeggie(
        name='Potato',
        description='Fresh potatoes',
        price=1.5,
        type='Vegetable',
        stock_quantity=200,
        veg_name='Potato',
        staff_id=staff_member.id,
        weight=100.0,
        weight_per_kilo=1.5
    )
    db.session.add(weighted_veggie)
    db.session.flush()

    retrieved_weighted_veggie = WeightedVeggie.query.filter_by(veg_name='Potato').first()
    assert retrieved_weighted_veggie is not None
    assert retrieved_weighted_veggie.weight == 100.0

def test_pack_veggie_model(test_client, staff_member):
    """
    Test the PackVeggie model and its inheritance from Veggie.
    """
    pack_veggie = PackVeggie(
        name='Bell Pepper Pack',
        description='Pack of bell peppers',
        price=4.0,
        type='Vegetable',
        stock_quantity=30,
        veg_name='Bell Pepper',
        staff_id=staff_member.id,
        num_of_pack=10,
        price_per_pack=4.0
    )
    db.session.add(pack_veggie)
    db.session.flush()

    retrieved_pack_veggie = PackVeggie.query.filter_by(veg_name='Bell Pepper').first()
    assert retrieved_pack_veggie is not None
    assert retrieved_pack_veggie.num_of_pack == 10

def test_unit_price_veggie_model(test_client, staff_member):
    """
    Test the UnitPriceVeggie model and its inheritance from Veggie.
    """
    unit_price_veggie = UnitPriceVeggie(
        name='Cucumber',
        description='Fresh cucumbers',
        price=1.0,
        type='Vegetable',
        stock_quantity=100,
        veg_name='Cucumber',
        staff_id=staff_member.id,
        price_per_unit=1.0,
        quantity=100
    )
    db.session.add(unit_price_veggie)
    db.session.flush()

    retrieved_unit_price_veggie = UnitPriceVeggie.query.filter_by(veg_name='Cucumber').first()
    assert retrieved_unit_price_veggie is not None
    assert retrieved_unit_price_veggie.quantity == 100

def test_premade_box_model(test_client, staff_member):
    """
    Test the PremadeBox model and its method.
    """
    premade_box = PremadeBox(
        name='Veggie Box',
        description='A box of assorted veggies',
        price=0.0,  # Will be calculated
        type='Box',
        stock_quantity=10,
        box_size='Medium',
        num_of_boxes=2,
        staff_id=staff_member.id
    )
    db.session.add(premade_box)
    db.session.flush()

    expected_price = 10.0 * 1.5 * 2  # base_price * multiplier * num_of_boxes
    assert premade_box.box_price() == expected_price

def test_order_model(test_client, customer, staff_member):
    """
    Test the Order model and its relationships with Customer and Staff.
    """
    order = Order(
        order_customer=customer.id,
        staff_id=staff_member.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    db.session.add(order)
    db.session.flush()

    retrieved_order = Order.query.filter_by(order_number='O123').first()
    assert retrieved_order is not None
    assert retrieved_order.total_amount == 150.0

def test_order_line_model(test_client):
    """
    Test the OrderLine model and its relationship with Order and Item.
    """
    # Create item
    item = Item(
        name='Carrot',
        description='Fresh carrots',
        price=2.5,
        type='Vegetable',
        stock_quantity=100
    )
    db.session.add(item)
    db.session.flush()

    # Create order
    customer = Customer(
        first_name='Bob',
        last_name='Johnson',
        password='password123',
        username='bobjohnson',
        cust_address='123 Main St',
        cust_balance=100.0,
        cust_id='C123',
        max_owing=500.0,
        distance_from_store=10.0
    )
    db.session.add(customer)
    db.session.flush()

    order = Order(
        order_customer=customer.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    db.session.add(order)
    db.session.flush()

    # Create order line
    order_line = OrderLine(
        item_number=item.id,
        order_id=order.id,
        quantity=5,
        order_type='Regular'
    )
    db.session.add(order_line)
    db.session.flush()

    retrieved_order_line = OrderLine.query.filter_by(order_id=order.id).first()
    assert retrieved_order_line is not None
    assert retrieved_order_line.quantity == 5
    assert retrieved_order_line.item.name == 'Carrot'

def test_payment_model(test_client, customer):
    """
    Test the Payment model and its relationships with Customer and Order.
    """
    # Create order
    order = Order(
        order_customer=customer.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    db.session.add(order)
    db.session.flush()

    payment = Payment(
        payment_amount=150.0,
        payment_method='CreditCard',
        payment_id='P123',
        customer_id=customer.id,
        order_id=order.id
    )
    db.session.add(payment)
    db.session.flush()

    retrieved_payment = Payment.query.filter_by(payment_id='P123').first()
    assert retrieved_payment is not None
    assert retrieved_payment.payment_amount == 150.0

def test_credit_card_payment_model(test_client, customer):
    """
    Test the CreditCardPayment model and its inheritance from Payment.
    """
    # Create order
    order = Order(
        order_customer=customer.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    db.session.add(order)
    db.session.flush()

    credit_payment = CreditCardPayment(
        payment_amount=150.0,
        payment_method='CreditCard',
        payment_id='P456',
        customer_id=customer.id,
        order_id=order.id,
        card_expiry_date='12/25',
        card_number='1234567890123456',
        card_type='Visa'
    )
    db.session.add(credit_payment)
    db.session.flush()

    retrieved_credit_payment = CreditCardPayment.query.filter_by(payment_id='P456').first()
    assert retrieved_credit_payment is not None
    assert retrieved_credit_payment.card_type == 'Visa'

def test_debit_card_payment_model(test_client, customer):
    """
    Test the DebitCardPayment model and its inheritance from Payment.
    """
    # Create order
    order = Order(
        order_customer=customer.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    db.session.add(order)
    db.session.flush()

    debit_payment = DebitCardPayment(
        payment_amount=150.0,
        payment_method='DebitCard',
        payment_id='P789',
        customer_id=customer.id,
        order_id=order.id,
        bank_name='Bank of World',
        debit_card_number='6543210987654321'
    )
    db.session.add(debit_payment)
    db.session.flush()

    retrieved_debit_payment = DebitCardPayment.query.filter_by(payment_id='P789').first()
    assert retrieved_debit_payment is not None
    assert retrieved_debit_payment.bank_name == 'Bank of World'

# -------------------------
# Testing Relationships
# -------------------------

def test_order_relationships(test_client, customer, staff_member):
    """
    Test relationships between Order, Customer, Staff, OrderLine, and Item.
    """
    # Create items
    item1 = Item(
        name='Lettuce',
        description='Fresh lettuce',
        price=1.5,
        type='Vegetable',
        stock_quantity=100
    )
    item2 = Item(
        name='Cucumber',
        description='Organic cucumber',
        price=2.0,
        type='Vegetable',
        stock_quantity=80
    )
    db.session.add(item1)
    db.session.add(item2)
    db.session.flush()

    # Create order
    order = Order(
        order_customer=customer.id,
        staff_id=staff_member.id,
        order_number='O456',
        order_status='Pending',
        total_amount=50.0
    )
    db.session.add(order)
    db.session.flush()

    # Create order lines
    order_line1 = OrderLine(
        item_number=item1.id,
        order_id=order.id,
        quantity=10
    )
    order_line2 = OrderLine(
        item_number=item2.id,
        order_id=order.id,
        quantity=5
    )
    db.session.add(order_line1)
    db.session.add(order_line2)
    db.session.flush()

    # Verify relationships
    retrieved_order = Order.query.filter_by(order_number='O456').first()
    assert len(retrieved_order.order_lines) == 2
    assert retrieved_order.customer.username == 'bobjohnson'
    assert retrieved_order.staff.username == 'alicesmith'

def test_customer_order_relationship(test_client, customer):
    """
    Test that orders are correctly linked to customers.
    """
    # Create orders
    order1 = Order(
        order_customer=customer.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    order2 = Order(
        order_customer=customer.id,
        order_number='O456',
        order_status='Pending',
        total_amount=50.0
    )
    db.session.add(order1)
    db.session.add(order2)
    db.session.flush()

    assert len(customer.list_of_orders) >= 2  # O123 and O456
    order_numbers = [order.order_number for order in customer.list_of_orders]
    assert 'O123' in order_numbers
    assert 'O456' in order_numbers

def test_staff_order_relationship(test_client, staff_member):
    """
    Test that orders are correctly linked to staff.
    """
    # Create customer
    customer = Customer(
        first_name='Bob',
        last_name='Johnson',
        password='password123',
        username='bobjohnson',
        cust_address='123 Main St',
        cust_balance=100.0,
        cust_id='C123',
        max_owing=500.0,
        distance_from_store=10.0
    )
    db.session.add(customer)
    db.session.flush()

    # Create orders
    order1 = Order(
        order_customer=customer.id,
        staff_id=staff_member.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    order2 = Order(
        order_customer=customer.id,
        staff_id=staff_member.id,
        order_number='O456',
        order_status='Pending',
        total_amount=50.0
    )
    db.session.add(order1)
    db.session.add(order2)
    db.session.flush()

    assert len(staff_member.list_of_orders) >= 2  # O123 and O456
    order_numbers = [order.order_number for order in staff_member.list_of_orders]
    assert 'O123' in order_numbers
    assert 'O456' in order_numbers

def test_payment_order_relationship(test_client):
    """
    Test that payments are correctly linked to orders.
    """
    # Create customer
    customer = Customer(
        first_name='Bob',
        last_name='Johnson',
        password='password123',
        username='bobjohnson',
        cust_address='123 Main St',
        cust_balance=100.0,
        cust_id='C123',
        max_owing=500.0,
        distance_from_store=10.0
    )
    db.session.add(customer)
    db.session.flush()

    # Create order
    order = Order(
        order_customer=customer.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    db.session.add(order)
    db.session.flush()

    # Create payment
    payment = Payment(
        payment_amount=150.0,
        payment_method='CreditCard',
        payment_id='P123',
        customer_id=customer.id,
        order_id=order.id
    )
    db.session.add(payment)
    db.session.flush()

    assert len(order.payments) >= 1
    payment_ids = [payment.payment_id for payment in order.payments]
    assert 'P123' in payment_ids

def test_item_order_line_relationship(test_client):
    """
    Test that items are correctly linked to order lines.
    """
    # Create item
    item = Item(
        name='Lettuce',
        description='Fresh lettuce',
        price=1.5,
        type='Vegetable',
        stock_quantity=100
    )
    db.session.add(item)
    db.session.flush()

    # Create customer and order
    customer = Customer(
        first_name='Bob',
        last_name='Johnson',
        password='password123',
        username='bobjohnson',
        cust_address='123 Main St',
        cust_balance=100.0,
        cust_id='C123',
        max_owing=500.0,
        distance_from_store=10.0
    )
    db.session.add(customer)
    db.session.flush()

    order = Order(
        order_customer=customer.id,
        order_number='O123',
        order_status='Pending',
        total_amount=150.0
    )
    db.session.add(order)
    db.session.flush()

    # Create order line
    order_line = OrderLine(
        item_number=item.id,
        order_id=order.id,
        quantity=10
    )
    db.session.add(order_line)
    db.session.flush()

    assert len(item.order_lines) >= 1
    order_line = item.order_lines[0]
    assert order_line.quantity == 10

# -------------------------
# Edge Cases and Validation
# -------------------------

def test_missing_required_field(test_client):
    """
    Test that creating an object with missing required fields raises an exception.
    """
    customer = Customer(
        first_name='Test',
        last_name='User',
        password='password123',
        username='testuser_missing_field',
        cust_address=None,  # Required field set to None
        cust_balance=0.0,
        cust_id='C999',
        max_owing=1000.0,
        distance_from_store=5.0
    )
    db.session.add(customer)
    with pytest.raises(IntegrityError):
        db.session.flush()
    db.session.rollback()

def test_invalid_data_type(test_client):
    """
    Test that creating an object with an invalid data type raises an exception.
    """
    customer = Customer(
        first_name='Test',
        last_name='User',
        password='password123',
        username='testuser_invalid_type',
        cust_address='789 Pine St',
        cust_balance='invalid_float',  # Should be a float
        cust_id='C1000',
        max_owing=1000.0,
        distance_from_store=5.0
    )
    db.session.add(customer)
    with pytest.raises((DataError, ValueError)):
        db.session.flush()
    db.session.rollback()

def test_unique_constraint_violation(test_client):
    """
    Test that creating an object that violates a unique constraint raises an exception.
    """
    person1 = Person(
        first_name='Test',
        last_name='User',
        password='pass',
        username='duplicateuser'
    )
    db.session.add(person1)
    db.session.flush()

    person2 = Person(
        first_name='Test2',
        last_name='User2',
        password='pass',
        username='duplicateuser'  # Same username
    )
    db.session.add(person2)
    with pytest.raises(IntegrityError):
        db.session.flush()
    db.session.rollback()

def test_foreign_key_constraint(test_client):
    """
    Test that setting an invalid foreign key raises an exception.
    """
    order = Order(
        order_customer=9999,  # Non-existent customer ID
        order_number='O999',
        order_status='Pending',
        total_amount=100.0
    )
    db.session.add(order)
    with pytest.raises(IntegrityError):
        db.session.flush()
    db.session.rollback()

def test_null_not_nullable_field(test_client):
    """
    Test that setting a non-nullable field to None raises an exception.
    """
    payment = Payment(
        payment_amount=100.0,
        payment_method=None,  # Non-nullable field
        payment_id='PInvalid',
        customer_id=1,
        order_id=1
    )
    db.session.add(payment)
    with pytest.raises(IntegrityError):
        db.session.flush()
    db.session.rollback()

def test_premade_box_price_method(test_client, staff_member):
    """
    Test the box_price method of the PremadeBox model.
    """
    premade_box = PremadeBox(
        name='Veggie Box Large',
        description='A large box of assorted veggies',
        price=0.0,  # Will be calculated
        type='Box',
        stock_quantity=5,
        box_size='Large',
        num_of_boxes=3,
        staff_id=staff_member.id
    )
    db.session.add(premade_box)
    db.session.flush()

    expected_price = 10.0 * 2.0 * 3  # base_price * multiplier * num_of_boxes
    assert premade_box.box_price() == expected_price

def test_zero_stock_quantity(test_client):
    """
    Test creating an item with zero stock quantity.
    """
    item = Item(
        name='OutOfStockItem',
        description='Item with zero stock',
        price=5.0,
        type='Test',
        stock_quantity=0
    )
    db.session.add(item)
    db.session.flush()

    retrieved_item = Item.query.filter_by(name='OutOfStockItem').first()
    assert retrieved_item is not None
    assert retrieved_item.stock_quantity == 0

def test_null_optional_field(test_client):
    """
    Test that setting an optional field to None does not raise an exception.
    """
    person = Person(
        first_name='Optional',
        last_name='Field',
        password='password123',
        username='optionalfield'
    )
    # Assuming 'middle_name' is an optional field
    person.middle_name = None
    db.session.add(person)
    db.session.flush()

    retrieved_person = Person.query.filter_by(username='optionalfield').first()
    assert retrieved_person is not None

def test_invalid_foreign_key_relationship(test_client):
    """
    Test that deleting a parent object affects the child due to foreign key constraints.
    """
    customer = Customer(
        first_name='Parent',
        last_name='Customer',
        password='password123',
        username='parentcustomer',
        cust_address='123 Parent St',
        cust_balance=0.0,
        cust_id='CParent',
        max_owing=1000.0,
        distance_from_store=5.0
    )
    db.session.add(customer)
    db.session.flush()

    order = Order(
        order_customer=customer.id,
        order_number='OParent',
        order_status='Pending',
        total_amount=50.0
    )
    db.session.add(order)
    db.session.flush()

    # Delete the customer
    db.session.delete(customer)
    with pytest.raises(IntegrityError):
        db.session.flush()
    db.session.rollback()

# --------------------------------------------
# Run the Tests
# --------------------------------------------

if __name__ == "__main__":
    pytest.main(["-v", __file__])