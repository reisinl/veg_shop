# pytest/route_test.py
import sys, os
from pathlib import Path
from sqlalchemy import text
# Get the parent directory of the current file (model_test.py)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
current_dir = os.path.abspath(os.path.dirname(__file__))
templates_dir = os.path.join(current_dir, 'templates')
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)
import pytest
from datetime import datetime
from models import (
    Person, Staff, Customer, CorporateCustomer, Item, UnitPriceVeggie,
    Order, Payment
)
from models import db
from main import Initialize_app


# # --------------------------------------------
# # Fixtures
# # --------------------------------------------
@pytest.fixture(scope='function')
def test_client():
    """
    Pytest fixture to set up a Flask test client with a MySQL test database.
    """
    app = Initialize_app()
    testing_client = app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield testing_client
        db.session.remove()
        db.drop_all()


def place_dummy_order(test_client, user_type):
    reset_database(1)
    item = Item.query.filter_by(id=1).first()

    response = None
    form_data = {}
    # Staff places an order for customer
    if user_type == "customer":
        form_data={
            f'order_{item.id}': item.id,
            f'order_type_{item.id}': 'unit'
        }
        login(test_client, '111', '123')
        
    else:
        form_data={
            'customer_id': str(1),
            f'order_{item.id}': '2',
            f'order_type_{item.id}': 'unit'
        }
        login(test_client, '333', '123')
    response = test_client.post('/place_order', data=form_data, follow_redirects=True)
    return response

def reset_database(reset_flg):
    """Reset database by executing SQL script using SQLAlchemy connection."""
    THIS_FOLDER = Path(__file__).parent.resolve()
    sql_file = "pytest_data.sql"
    if reset_flg == 0:
        sql_file = "pytest_data_reset.sql"
    with open(THIS_FOLDER / sql_file, 'r') as f:
        sql_statements = f.read()
    with db.engine.connect() as connection:
        with connection.begin():
            for statement in sql_statements.split(';'):
                if statement.strip():
                    connection.execute(text(statement)) 

def create_user(username, password, user_type='customer', first_name='First', last_name='Last', max_owing=500):

    if user_type == 'customer':
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            cust_address='123 Test St',
            cust_balance=100.0,
            cust_id='C123',
            max_owing=max_owing,
            distance_from_store=10.0
        )
        db.session.add(customer)
        db.session.flush()
        return customer
    elif user_type == 'corporate':
        customer = CorporateCustomer(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            cust_address='123 Corporate St',
            cust_balance=1000.0,
            cust_id='C456',
            max_owing=5000.0,
            distance_from_store=15.0,
            discount_rate=0.1,
            max_credit=5000.0,
            min_balance=1000.0
        )
        db.session.add(customer)
        db.session.flush()
        return customer
    elif user_type == 'staff':
        staff = Staff(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            date_joined=datetime.now(),
            dept_name='Sales',
            staff_id='S123'
        )
        db.session.add(staff)
        db.session.flush()
        return staff

def create_item(name='Carrot', price=2.0, stock_quantity=100, item_type='Veggie', staff_id=3):
    
    item = None
    if item_type == "new":
        item = UnitPriceVeggie (
            name=name,
            description=f'Fresh {name}',
            price=price,
            type="Veggie",
            stock_quantity=stock_quantity,
            veg_name = name,
            staff_id = staff_id,
            price_per_unit = 3.0,
            quantity = 3
        )
    else:
        item = Item(
            name=name,
            description=f'Fresh {name}',
            price=price,
            type=item_type,
            stock_quantity=stock_quantity
        )

    db.session.add(item)
    db.session.flush()
    return item

def login(test_client, username, password):
    return test_client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

# --------------------------------------------
# Test Functions
# --------------------------------------------

def test_home_page(test_client):
    """
    Test the home page.
    """
    reset_database(0)
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"home" in response.data.lower()

def test_login_success(test_client):
    """
    Test logging in with valid credentials.
    """
    person = Person(username="testuser", password="testpass", first_name="first_name", last_name="last_name")
    db.session.add(person)
    db.session.flush()

    response = login(test_client, 'testuser', 'testpass')
    assert response.status_code == 200
    assert b"logged in successfully" in response.data.lower()

    with test_client.session_transaction() as sess:
        assert sess['user_id'] is not None

def test_login_failure(test_client):
    """
    Test logging in with invalid credentials.
    """
    response = login(test_client, 'nonexistent', 'wrongpass')
    assert response.status_code == 200
    assert b"invalid credentials" in response.data.lower()

def test_logout(test_client):
    """
    Test logging out.
    """
    person = Person(username="testuser", password="testpass", first_name="first_name", last_name="last_name")
    db.session.add(person)
    db.session.flush()
    login(test_client, 'testuser', 'testpass')

    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"logged out successfully" in response.data.lower()

    with test_client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'user_type' not in sess

def test_dashboard_no_login(test_client):
    """
    Test accessing the dashboard without logging in.
    """
    response = test_client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"please log in to access the dashboard" in response.data.lower()

def test_dashboard_with_login(test_client):
    """
    Test accessing the dashboard after logging in.
    """
    create_user('testuser', 'testpass', user_type='customer')
    login(test_client, 'testuser', 'testpass')

    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b"dashboard" in response.data.lower()

def test_view_vegetables(test_client):
    """
    Test viewing vegetables and boxes.
    """
    create_user('testuser', 'testpass', user_type='customer')
    login(test_client, 'testuser', 'testpass')

    # Create test items
    create_item('Carrot', 2.0, 100, 'Veggie')
    create_item('Veggie Box', 20.0, 50, 'Box')

    response = test_client.get('/vegetables')
    assert response.status_code == 200
    assert b"carrot" in response.data.lower()
    assert b"veggie box" in response.data.lower()

def test_place_order_customer(test_client):
    """
    Test a customer placing an order.
    """
    response = place_dummy_order(test_client, "customer")

    assert response.status_code == 200
    
    # Verify that the order was created
    orders = Order.query.filter_by(order_customer=1).all()
    assert len(orders) == 1
    assert orders[0].total_amount > 0

def test_place_order_staff(test_client):
    """
    Test a staff member placing an order for a customer.
    """
    # Staff places order on behalf of customer
    response = place_dummy_order(test_client, "staff")

    assert response.status_code == 200

    # Verify order creation
    orders = Order.query.filter_by(order_customer=1).all()
    assert len(orders) == 1
    assert orders[0].staff_id == 3

def test_place_order_insufficient_stock(test_client):
    """
    Test placing an order when there is insufficient stock.
    """
    create_user('customer3', 'custpass', user_type='customer')
    item = create_item('Cucumber', 0.5, 5, 'Veggie')  # Only 5 in stock
    login(test_client, 'customer3', 'custpass')

    response = test_client.post('/place_order', data={
        f'order_{item.id}': '10',  # Attempting to order 10
        f'order_type_{item.id}': 'unit'
    }, follow_redirects=True)

    assert response.status_code == 200


def test_checkout(test_client):
    """
    Test the checkout process.
    """
    place_dummy_order(test_client, "customer")

    order = Order.query.filter_by(order_customer=1).first()
    assert order is not None

    # Proceed to checkout
    response = test_client.post(f'/checkout/{order.id}', data={
        'payment_method': 'Credit Card',
        'payment_amount': str(order.total_amount),
        'card_number': '4111111111111111',
        'card_expiry_date': '12/25',
        'card_type': 'Visa'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Verify payment and order status
    payment = Payment.query.filter_by(order_id=order.id).first()
    assert payment is not None
    assert order.order_status == 'Completed'

def test_view_my_orders(test_client):
    """
    Test viewing orders for a customer.
    """
    place_dummy_order(test_client, "customer")

    response = test_client.get(f'/my_orders/{1}')
    assert response.status_code == 200
    assert b"carrot by unit - quantity: 1" in response.data.lower()

def test_view_current_orders(test_client):
    """
    Test viewing current (pending) orders.
    """
    customer = create_user('customer6', 'custpass', user_type='customer')
    login(test_client, 'customer6', 'custpass')

    response = test_client.get('/current_orders')
    assert response.status_code == 200
    assert b"current orders" in response.data.lower()

def test_view_previous_orders(test_client):
    """
    Test viewing previous (completed) orders.
    """
    place_dummy_order(test_client, "customer")
    order = Order.query.filter_by(order_customer=1).first()
    test_client.post(f'/checkout/{order.id}', data={
        'payment_method': 'Credit Card',
        'payment_amount': str(order.total_amount),
        'card_number': '4111111111111111',
        'card_expiry_date': '12/25',
        'card_type': 'Visa'
    }, follow_redirects=True)

    response = test_client.get('/previous_orders')
    assert response.status_code == 200
    assert b"completed" in response.data.lower()

def test_cancel_order(test_client):
    """
    Test cancelling a pending order.
    """
    place_dummy_order(test_client, "customer")
    order = Order.query.filter_by(order_customer=1).first()

    # Cancel the order
    response = test_client.post(f'/cancel_order/{order.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"order canceled successfully" in response.data.lower()

    # Verify that the order is deleted
    order = Order.query.get(order.id)
    assert order is None

def test_customer_details(test_client):
    """
    Test viewing customer details.
    """
    customer = create_user('customer9', 'custpass', first_name="customer_9", user_type='customer')
    login(test_client, 'customer9', 'custpass')

    response = test_client.get('/customer_details')
    assert response.status_code == 200
    assert b"customer_9" in response.data.lower()

def test_update_order_status(test_client):
    """
    Test updating an order status as staff.
    """
    place_dummy_order(test_client, "staff")
    order = Order.query.filter_by(order_customer=1).first()

    # Update order status
    response = test_client.post(f'/update_order_status/{order.id}', data={
        'order_status': 'Shipped'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"order status updated successfully" in response.data.lower()

    # Verify order status
    order = Order.query.get(order.id)
    assert order.order_status == 'Shipped'

def test_view_customers(test_client):
    """
    Test viewing all customers as staff.
    """
    staff = create_user('staff3', 'staffpass', user_type='staff')
    create_user('customer11', 'custpass', user_type='customer')
    create_user('customer12', 'custpass', user_type='corporate')
    login(test_client, 'staff3', 'staffpass')

    response = test_client.get('/customers')
    assert response.status_code == 200
    assert b"customer" in response.data.lower()
    assert b"corporate" in response.data.lower()

def test_generate_customer_list(test_client):
    """
    Test generating customer list as CSV.
    """
    create_user('staff4', 'staffpass', user_type='staff')
    create_user('customer13', 'custpass', user_type='customer')
    login(test_client, 'staff4', 'staffpass')

    response = test_client.get('/generate_customer_list')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b"Customer ID,First Name,Last Name,Address,Balance" in response.data

def test_generate_report(test_client):
    """
    Test generating sales report.
    """
    create_user('staff5', 'staffpass', user_type='staff')
    login(test_client, 'staff5', 'staffpass')

    response = test_client.get('/generate_report')
    assert response.status_code == 200
    assert b"report" in response.data.lower()

def test_view_popular_items(test_client):
    """
    Test viewing most popular items.
    """
    reset_database(0)
    staff = create_user('staff6', 'staffpass', user_type='staff')
    customer = create_user('customer14', 'custpass', user_type='customer', max_owing=10)
    item = create_item(name='Eggplant', price=2.5, stock_quantity=100,item_type="new", staff_id=staff.id)
    login(test_client, 'customer14', 'custpass')
    # Place an order
    response=test_client.post('/place_order', data={
        f'order_{item.id}': item.id,
        f'order_type_{item.id}': 'unit'
    }, follow_redirects=True)

    login(test_client, 'staff6', 'staffpass')
    response = test_client.get('/popular_items')
    assert response.status_code == 200
    assert b"eggplant" in response.data.lower()

def test_customer_access_staff_routes(test_client):
    """
    Test that customers cannot access staff-only routes.
    """
    create_user('customer15', 'custpass', user_type='customer')
    login(test_client, 'customer15', 'custpass')

    response = test_client.get('/customers', follow_redirects=True)
    assert response.status_code == 200
    assert b"access denied" in response.data.lower()

def test_staff_access_customer_routes(test_client):
    """
    Test that staff can access staff and customer routes.
    """
    create_user('staff7', 'staffpass', user_type='staff')
    login(test_client, 'staff7', 'staffpass')

    response = test_client.get('/customers')
    assert response.status_code == 200
    assert b"customers" in response.data.lower()

    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b"dashboard" in response.data.lower()

def test_checkout_insufficient_balance(test_client):
    """
    Test the checkout process with insufficient account balance.
    """
    place_dummy_order(test_client, "customer")
    
    customer = Customer.query.filter_by(id=1).first()
    customer.cust_balance = 1.0  # Set a low balance to simulate insufficient funds
    db.session.flush()
    login(test_client, 'customer16', 'custpass')

    # Place an order
    
    order = Order.query.filter_by(order_customer=1).first()
    response = test_client.post(f'/checkout/{order.id}', data={
        'payment_method': 'Account',
        'payment_amount': str(order.total_amount)
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"insufficient account balance" in response.data.lower()

def test_generate_weekly_report(test_client):
    """
    Test generating a weekly sales report.
    """
    staff = create_user('staff8', 'staffpass', user_type='staff')
    login(test_client, 'staff8', 'staffpass')

    response = test_client.post('/generate_report', data={
        'report_type': 'weekly'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"weekly" in response.data.lower()

def test_generate_monthly_report(test_client):
    """
    Test generating a monthly sales report.
    """
    staff = create_user('staff9', 'staffpass', user_type='staff')
    login(test_client, 'staff9', 'staffpass')

    response = test_client.post('/generate_report', data={
        'report_type': 'monthly'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"monthly" in response.data.lower()

def test_generate_yearly_report(test_client):
    """
    Test generating an yearly sales report.
    """
    staff = create_user('staff10', 'staffpass', user_type='staff')
    login(test_client, 'staff10', 'staffpass')

    response = test_client.post('/generate_report', data={
        'report_type': 'yearly'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"yearly" in response.data.lower()
# --------------------------------------------
# Run the Tests
# --------------------------------------------

if __name__ == "__main__":
    pytest.main(["-v", __file__])
