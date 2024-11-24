from flask import render_template, request, redirect, url_for, flash, session, Response
from models import Person, Staff, Customer, CorporateCustomer, Order, OrderLine, Item, Payment, CreditCardPayment, DebitCardPayment, PremadeBox, WeightedVeggie, PackVeggie, UnitPriceVeggie
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import joinedload

def setup_routes(app, db):
    # Home Page
    @app.route("/")
    def home():
        # Render the home page template
        return render_template("home.html")

    # Login Page for Staff and Customer
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            # Fetch login credentials from the form
            username = request.form["username"]
            password = request.form["password"]
            # Check if the credentials match an existing user
            person = Person.query.filter_by(username=username, password=password).first()
            if person:
                # Store user information in session
                session['user_id'] = person.id
                # Determine user type (staff or customer)
                if Staff.query.filter_by(id=person.id).first():
                    session['user_type'] = 'staff'
                elif Customer.query.filter_by(id=person.id).first():
                    session['user_type'] = 'customer'
                flash("Logged in successfully!", "success")
                return redirect(url_for("dashboard"))
            else:
                # Invalid credentials
                flash("Invalid credentials. Please try again.", "danger")
        # Render the login page
        return render_template("login.html")

    # Logout Functionality
    @app.route("/logout")
    def logout():
        # Clear session to log out user
        session.clear()
        flash("Logged out successfully!", "success")
        return redirect(url_for("login"))

    # Dashboard (Accessible only to logged-in users)
    @app.route("/dashboard")
    def dashboard():
        if 'user_id' not in session:
            flash("Please log in to access the dashboard.", "danger")
            return redirect(url_for("login"))
        # Get the user details from the session
        user = Person.query.get(session['user_id'])
        return render_template("dashboard.html", user=user)

    # View Available Vegetables and Boxes
    @app.route("/vegetables")
    def view_vegetables():
        if 'user_id' not in session:
            flash("Please log in to access the dashboard.", "danger")
            return redirect(url_for("login"))
        # Fetch only items that are either vegetables or boxes
        items = Item.query.filter(Item.type.in_(['Veggie', 'Box'])).all()
        return render_template("vegetables.html", items=items)

    # Place Order Functionality
    @app.route("/place_order", methods=["GET", "POST"])
    def place_order():
        if 'user_id' not in session:
            flash("Please log in to place an order.", "danger")
            return redirect(url_for("login"))

        user_id = session['user_id']
        customer = None
        staff = None
        staff_id = None

        # Check if the logged-in user is staff
        if 'user_type' in session and session['user_type'] == 'staff':
            if request.method == "POST" and "customer_id" in request.form:
                # Allow staff to select a customer to place order for
                customer_id = int(request.form.get("customer_id"))
                customer = Customer.query.get(customer_id)
            elif request.method == "GET":
                # Staff accessing order page for the first time, show all customers
                return render_template("place_order.html", available_items=Item.query.all(), customer=None, staff=True, all_customers=Customer.query.all())
            staff = True
            staff_id = user_id
        else:
            # If the logged-in user is a customer, they can only order for themselves
            customer_id = user_id
            customer = Customer.query.get(customer_id)
            staff = False

        # Redirect if customer not found
        if not customer:
            flash("You need to be a customer to place an order or select a customer to place an order on their behalf.", "danger")
            return redirect(url_for("dashboard"))

        available_items = Item.query.filter(Item.type.in_(['Veggie'])).all()

        # Check for corporate customers and their credit limit
        corp_customer = CorporateCustomer.query.filter_by(id=customer.id).first()
        if corp_customer:
            if customer.cust_balance < corp_customer.max_credit:
                flash("Corporate customers cannot place orders if their balance is less than their credit limit.", "danger")
                return redirect(url_for("dashboard"))

        # Check private customer's maximum outstanding balance
        if customer.max_owing > 100:
            flash("The private customer cannot place orders if the customer's amount owing exceeds $100.", "danger")
            return redirect(url_for("dashboard"))

        if request.method == "POST" and ("box_size" in request.form or any(request.form.get(f"order_{item.id}") for item in available_items)):
            try:
                # Calculate total price for the order
                total_price = 0.0
                order_lines = []

                # Handle Premade Box Orders
                box_size = request.form.get("box_size")
                num_of_boxes = int(request.form.get("num_of_boxes", 0))
                if num_of_boxes > 0:
                    premade_box_price = 10.0 if box_size == 'Small' else 15.0 if box_size == 'Medium' else 20.0
                    total_price += premade_box_price * num_of_boxes
                    premade_box = PremadeBox.query.filter_by(box_size=box_size).first()
                    if not premade_box:
                        flash("The selected box size is not available.", "danger")
                        return redirect(url_for("place_order"))
                    order_lines.append(OrderLine(item_number=premade_box.id, quantity=num_of_boxes))

                # Handle Individual Vegetable Orders
                with db.session.no_autoflush:
                    for item in available_items:
                        order_type = request.form.get(f"order_type_{item.id}")
                        quantity = request.form.get(f"order_{item.id}", 0, type=int)
                        quantity_ordered = quantity
                        if quantity > 0:
                            # Calculate based on order type (unit, weight, or pack)
                            if order_type == 'unit':
                                unit_veggie = UnitPriceVeggie.query.get(item.id)
                                total_price += unit_veggie.price_per_unit * quantity
                                quantity_ordered = unit_veggie.quantity * quantity
                            elif order_type == 'weight':
                                weight_veggie = WeightedVeggie.query.get(item.id)
                                total_price += weight_veggie.weight_per_kilo * quantity
                                quantity_ordered = weight_veggie.weight * quantity
                            elif order_type == 'pack':
                                pack_veggie = PackVeggie.query.get(item.id)
                                total_price += pack_veggie.price_per_pack * quantity
                                quantity_ordered = pack_veggie.num_of_pack * quantity
                            else:
                                total_price += item.price * quantity

                            # Stock Check
                            if item.stock_quantity < quantity_ordered:
                                flash(f"Item {item.name} does not have enough stock. Available: {item.stock_quantity}", "danger")
                                return redirect(url_for("place_order"))

                            # Update item stock
                            item.stock_quantity -= quantity_ordered
                            db.session.add(item)
                            order_lines.append(OrderLine(item_number=item.id, quantity=quantity, order_type=order_type))

                # Apply discount for corporate customers
                if corp_customer:
                    total_price *= 0.9  # Apply 10% discount

                # Add delivery fee if applicable
                delivery = request.form.get("delivery") if customer.distance_from_store <= 20 else 'No'
                if delivery == 'Yes':
                    delivery_fee = 10.0
                    total_price += delivery_fee

                # Create new order
                order_number = "ORD" + str(int(datetime.now().timestamp()))
                new_order = Order(
                    order_customer=customer.id, 
                    staff_id=staff_id, 
                    order_date=datetime.now(), 
                    order_number=order_number, 
                    order_status="Pending", 
                    total_amount=total_price)
                db.session.add(new_order)
                db.session.commit()

                # Add order lines to the order
                for order_line in order_lines:
                    order_line.order_id = new_order.id
                    db.session.add(order_line)
                db.session.commit()

                flash(f"Order placed successfully! Total price: ${total_price:.2f}. You can proceed to payment now or later from your orders page.", "success")
                return redirect(url_for("checkout", order_id=new_order.id))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while placing the order: {str(e)}", "danger")
                return redirect(url_for("place_order"))

        # Render order placement form
        return render_template("place_order.html", available_items=available_items, customer=customer, staff=staff, all_customers=Customer.query.all())

    # Checkout Page
    @app.route("/checkout/<int:order_id>", methods=["GET", "POST"])
    def checkout(order_id):
        if 'user_id' not in session:
            flash("Please log in to proceed to checkout.", "danger")
            return redirect(url_for("login"))
        
        order = Order.query.get(order_id)
        if not order:
            flash("Order not found.", "danger")
            return redirect(url_for("dashboard"))
        
        customer = Customer.query.get(order.order_customer)
        payment_due_amount = order.total_amount - sum(payment.payment_amount for payment in order.payments)
        
        if request.method == "POST":
            payment_method = request.form.get("payment_method")
            payment_amount = float(request.form.get("payment_amount", 0))
            payment_id = order.order_number
            new_payment = None

            try:
                # Handle payment logic
                if payment_method == "Credit Card":
                    new_payment = CreditCardPayment(
                        payment_amount=payment_amount,
                        payment_date=datetime.now(),
                        payment_method="Credit Card",
                        payment_id=payment_id,
                        customer_id=order.order_customer,
                        card_number=request.form.get("card_number"),
                        card_expiry_date=request.form.get("card_expiry_date"),
                        card_type=request.form.get("card_type"),
                        order_id=order.id
                    )
                elif payment_method == "Debit Card":
                    new_payment = DebitCardPayment(
                        payment_amount=payment_amount,
                        payment_date=datetime.now(),
                        payment_method="Debit Card",
                        payment_id=payment_id,
                        customer_id=order.order_customer,
                        debit_card_number=request.form.get("debit_card_number"),
                        bank_name=request.form.get("bank_name"),
                        order_id=order.id
                    )
                elif payment_method == "Account":
                    if customer and customer.cust_balance >= payment_amount:
                        customer.cust_balance -= payment_amount
                        new_payment = Payment(
                            payment_amount=payment_amount,
                            payment_date=datetime.now(),
                            payment_method="Account",
                            payment_id=payment_id,
                            customer_id=customer.id,
                            order_id=order.id
                        )
                        db.session.add(customer)
                    else:
                        flash("Insufficient account balance.", "danger")
                        return redirect(url_for("checkout", order_id=order.id))

                if new_payment:
                    db.session.add(new_payment)
                    db.session.commit()
                    
                    # Update order status if fully paid
                    payment_due_amount -= payment_amount
                    if payment_due_amount <= 0:
                        order.order_status = "Completed"
                    
                    db.session.commit()
                    flash("Payment successful! Order completed.", "success")
                    return redirect(url_for("my_orders", order_id=order.id))
                else:
                    flash("Invalid payment method.", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred during payment: {str(e)}", "danger")
                return redirect(url_for("checkout", order_id=order.id))

        return render_template("checkout.html", order=order, customer=customer, payment_due_amount=payment_due_amount)

    # View Orders for Customer
    @app.route('/my_orders/<int:order_id>', methods=['GET'])
    def my_orders(order_id=None):
        if 'user_id' not in session:
            flash("Please log in to view your orders.", "danger")
            return redirect(url_for('login'))

        user_id = session['user_id']
        customer = Customer.query.get(user_id)

        if not customer:
            flash("You need to be a customer to view your orders.", "danger")
            return redirect(url_for('dashboard'))

        # Fetch order details with items and payments for a specific order or all orders for the user
        orders = (
            Order.query.filter_by(id=order_id)
            .options(joinedload(Order.order_lines).joinedload(OrderLine.item)).all()
            if order_id
            else Order.query.filter_by(order_customer=user_id)
            .options(joinedload(Order.order_lines).joinedload(OrderLine.item)).all()
        )

        order_details = []
        for order in orders:
            order_lines = OrderLine.query.filter_by(order_id=order.id).all()
            payment = Payment.query.filter_by(order_id=order.id).first()
            person = Person.query.get(order.order_customer)
            customer_name = f"{person.first_name} {person.last_name}" if person else None
            order_details.append({
                'order': order,
                'order_lines': order_lines,
                'payment': payment,
                'customer_name': customer_name
            })
        
        return render_template('my_orders.html', orders=order_details)

    # View Current Orders (Pending)
    @app.route("/current_orders")
    def view_current_orders():
        if 'user_id' not in session:
            flash("Please log in to view orders.", "danger")
            return redirect(url_for("login"))
        orders = Order.query.filter_by(order_status='Pending')
        # Customers only see their own pending orders
        orders = orders.filter_by(order_customer=session['user_id']).all() if session['user_type'] == 'customer' else orders.all()
        return render_template("current_orders.html", orders=orders)

    # View Previous Orders (Completed)
    @app.route("/previous_orders")
    def view_previous_orders():
        if 'user_id' not in session:
            flash("Please log in to view orders.", "danger")
            return redirect(url_for("login"))
        orders = Order.query.filter(Order.order_status != 'Pending')
        # Customers only see their own completed orders
        orders = orders.filter_by(order_customer=session['user_id']).all() if session['user_type'] == 'customer' else orders.all()
        return render_template("previous_orders.html", orders=orders)

    # Cancel Pending Order (Customer Only)
    @app.route("/cancel_order/<int:order_id>", methods=["POST"])
    def cancel_order(order_id):
        if 'user_id' not in session:
            flash("Please log in to cancel an order.", "danger")
            return redirect(url_for("login"))
        
        try:
            order = Order.query.get(order_id)
            # Only allow cancellation if the order is pending and belongs to the user
            if order and order.order_status == 'Pending' and order.order_customer == session['user_id']:
                # Delete associated OrderLine records before deleting the order
                OrderLine.query.filter_by(order_id=order.id).delete()
                db.session.delete(order)
                db.session.commit()
                flash("Order canceled successfully.", "success")
            else:
                flash("Unable to cancel order. Either it does not exist, or it has already been processed.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while trying to cancel the order: {str(e)}", "danger")

        return redirect(url_for("view_current_orders"))

    # Customer Details Page
    @app.route("/customer_details")
    def customer_details():
        if 'user_id' not in session:
            flash("Please log in to view your orders.", "danger")
            return redirect(url_for('login'))
        customer = Customer.query.get(session['user_id'])
        return render_template("customer_details.html", customer=customer)

    # Update Order Status (Staff Only)
    @app.route("/update_order_status/<int:order_id>", methods=["POST"])
    def update_order_status(order_id):
        if 'user_id' not in session or session['user_type'] != 'staff':
            flash("Access denied.", "danger")
            return redirect(url_for("login"))
        order = Order.query.get(order_id)
        if order:
            # Update the order status based on staff input
            order.order_status = request.form.get("order_status")
            db.session.commit()
            flash("Order status updated successfully.", "success")
        else:
            flash("Order not found.", "danger")
        return redirect(url_for("view_current_orders"))
    
    # View All Customers (Staff Only)
    @app.route("/customers", methods=["GET"])
    def view_customers():
        if 'user_id' not in session or session['user_type'] != 'staff':
            flash("Access denied. You need to be a staff member to view this page.", "danger")
            return redirect(url_for("login"))

        # Fetch all customers
        customers = Customer.query.all()
        customer_details = []
        for customer in customers:
            # Determine customer type (corporate or private)
            customer_type = "Corporate" if CorporateCustomer.query.filter_by(id=customer.id).first() else "Private"
            customer_details.append({
                "customer": customer,
                "type": customer_type
            })
        return render_template("view_customers.html", customers=customer_details)

    # Generate Customer List as CSV (Staff Only)
    @app.route("/generate_customer_list", methods=["GET"])
    def generate_customer_list():
        if 'user_id' not in session or session['user_type'] != 'staff':
            flash("Access denied. You need to be a staff member to view this page.", "danger")
            return redirect(url_for("login"))

        # Create a CSV response for all customers
        customers = Customer.query.all()
        def generate():
            yield "Customer ID,First Name,Last Name,Address,Balance\n"
            for customer in customers:
                yield f"{customer.id},{customer.first_name},{customer.last_name},{customer.cust_address},{customer.cust_balance}\n"

        return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=customer_list.csv"})
    
    # Generate Sales Report (Staff Only)
    @app.route("/generate_report", methods=["GET", "POST"])
    def generate_report():
        if 'user_id' not in session or session['user_type'] != 'staff':
            flash("Access denied. You need to be a staff member to view this page.", "danger")
            return redirect(url_for("login"))

        report_type = request.form.get('report_type', 'weekly') if request.method == "POST" else 'weekly'
        # Determine the start date based on report type
        start_date = datetime.now() - timedelta(weeks=1) if report_type == 'weekly' else datetime.now() - timedelta(days=30 if report_type == 'monthly' else 365)

        # Calculate total sales for the given time frame
        total_sales = db.session.query(func.sum(Payment.payment_amount)).filter(Payment.payment_date >= start_date).scalar() or 0

        # Fetch the top 5 most popular items
        # Query to determine the most popular items based on the number of order lines
        most_popular_items = (
            db.session.query(Item.name, func.count(OrderLine.item_number))
            # Join OrderLine to determine how many times each item has been ordered
            .join(OrderLine)
            # Group the results by item ID to aggregate counts per item
            .group_by(Item.id)
            # Order the results by the count of each item's appearances in descending order
            .order_by(func.count(OrderLine.item_number).desc())
            # Limit the results to the top 10 most popular items
            .limit(5)
            .all()
        )
        return render_template("report.html", report_type=report_type, total_sales=total_sales, most_popular_items=most_popular_items)
    
    # View Most Popular Items (Staff Only)
    @app.route("/popular_items", methods=["GET"])
    def view_popular_items():
        if 'user_id' not in session or session['user_type'] != 'staff':
            flash("Access denied. You need to be a staff member to view this page.", "danger")
            return redirect(url_for("login"))

        # Query to determine the most popular items based on the number of order lines
        most_popular_items = (
            db.session.query(Item.name, func.count(OrderLine.item_number))
            # Join OrderLine to determine how many times each item has been ordered
            .join(OrderLine)
            # Group the results by item ID to aggregate counts per item
            .group_by(Item.id)
            # Order the results by the count of each item's appearances in descending order
            .order_by(func.count(OrderLine.item_number).desc())
            # Limit the results to the top 10 most popular items
            .limit(10)
            .all()
        )
        return render_template("popular_items.html", most_popular_items=most_popular_items)
