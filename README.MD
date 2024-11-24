**Before the Start**
Please run the `table.sql` file to get the data ready for the whole project

**User Quick Start**
Please note the initial password for all users is `123`
**Private customer info to login**
`user_name`: `111`
**Corporate customer to login**
`user_name`: `666`
**Staff to login**
`user_name`: `333`

**Detailed Report on Flask Routes and Logic**

### 1. **Home Page Route**
```python
@app.route("/")
def home():
    return render_template("home.html")
```
- **Purpose**: Serves as the initial landing page for users visiting the application. It renders the `home.html` template, which contains basic information about the platform, such as introductory content, navigation links, and other essential details to guide the user.
- **Logic**:
  - The route is mapped to the base URL (`/`). This function simply renders a static HTML template (`home.html`). No specific processing is done here; it is meant to serve as an informational page to engage users before they interact further with the system.

### 2. **Login Route**
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        person = Person.query.filter_by(username=username, password=password).first()

        if person:
            session['user_id'] = person.id
            if Staff.query.filter_by(id=person.id).first():
                session['user_type'] = 'staff'
            elif Customer.query.filter_by(id=person.id).first():
                session['user_type'] = 'customer'
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")
```
- **Purpose**: Handles the authentication process for both staff and customers by validating user credentials against the database.
- **Logic**:
  - **POST Request**: Takes user credentials (`username` and `password`) from the form. If the user is found in the `Person` table, user information is stored in the session. The type of user is determined by checking the `Staff` and `Customer` tables.
    - If the user is a staff member, the session stores `'user_type'` as `'staff'`.
    - If the user is a customer, the session stores `'user_type'` as `'customer'`.
    - If authentication is successful, the user is redirected to the dashboard, and a success message will be displayed.
    - If the credentials are incorrect, an error message is flashed, and the login page is re-rendered.
  - **GET Request**: If accessed with a GET request, the function simply renders the login page (`login.html`).

### 3. **Logout Route**
```python
@app.route("/logout")
def logout():
    session.clear()  # Clears all session data to log out user
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))
```
- **Purpose**: Logs the user out by clearing all session data, ensuring that no sensitive user information remains active in the session.
- **Logic**:
  - The `session.clear()` function is used to remove all data from the current session, effectively logging out the user.
  - A flash message indicates successful logout to provide feedback to the user.
  - Redirects to the login page (`/login`) to allow the user to log back in or a different user to authenticate.

### 4. **Dashboard Route**
```python
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for("login"))
    user = Person.query.get(session['user_id'])
    return render_template("dashboard.html", user=user)
```
- **Purpose**: Displays the main dashboard for logged-in users, providing them with options to manage orders, view available items, and perform other actions based on their user role.
- **Logic**:
  - **Authentication Check**: Checks if a user is logged in by verifying the presence of `'user_id'` in the session. If not present, the user is redirected to the login page with an appropriate message.
  - **User Information Retrieval**: Retrieves user details from the `Person` table using the `user_id` from the session. This user information is then passed to the `dashboard.html` template to personalize the user's experience.
  - **Template Rendering**: Renders the `dashboard.html` page with the user information, enabling dynamic content based on user-specific data.

### 5. **View Vegetables Route**
```python
@app.route("/vegetables")
def view_vegetables():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for("login"))
    items = Item.query.filter(Item.type.in_(['Veggie', 'Box'])).all()
    return render_template("vegetables.html", items=items)
```
- **Purpose**: Allows users to view the list of available vegetables and box options that can be ordered.
- **Logic**:
  - **Authentication Check**: Redirects unauthenticated users to the login page.
  - **Item Query**: Queries the `Item` table for items with type `'Veggie'` or `'Box'` to filter out other product types. This query results in a list of available items that match the filter criteria.
  - **Template Rendering**: Passes the retrieved items to the `vegetables.html` template, which displays them in a user-friendly manner, allowing users to check available products.

### 6. **Place Order Route**
```python
@app.route("/place_order", methods=["GET", "POST"])
def place_order():
    if 'user_id' not in session:
        flash("Please log in to place an order.", "danger")
        return redirect(url_for("login"))
    # Order placement logic follows...
```
- **Purpose**: Handles placing orders for customers or staff members who are placing orders on behalf of customers.
- **Logic**:
  - **Authentication Check**: Ensures the user is logged in; otherwise, redirects them to the login page.
  - **Staff vs. Customer Handling**:
    - If the logged-in user is a staff member, they can select a customer for whom they want to place an order.
    - If the user is a customer, they can only place an order for themselves.
  - **Order Calculation and Creation**: Handles the calculation of the total order price, checking item availability in stock, applying corporate customer discounts if applicable, and creating an `Order` record along with associated `OrderLine` records in the database.
  - **Template Rendering**: Depending on the type of request (`GET` or `POST`), the order form may either be displayed or processed.

### 7. **Checkout Route**
```python
@app.route("/checkout/<int:order_id>", methods=["GET", "POST"])
def checkout(order_id):
    if 'user_id' not in session:
        flash("Please log in to proceed to checkout.", "danger")
        return redirect(url_for("login"))
    # Checkout logic follows...
```
- **Purpose**: Get the checkout process for an order, handling the payment process and allowing users to complete their purchase.
- **Logic**:
  - **Order Validation**: Retrieves the order details using `order_id` and validates that the order exists.
  - **Payment Calculation**: Computes the outstanding payment amount based on any previous payments made.
  - **Payment Handling**: Supports various payment methods (`Credit Card`, `Debit Card`, `Account`). Depending on the payment type, the system processes the payment accordingly, updating the order status to `"Completed"` if the payment is fully paid.
  - **Template Rendering**: Depending on whether it is a `GET` or `POST` request, the checkout page may either display the payment form or process payment information.

### 8. **View Orders (Customer) Route**

```python
@app.route('/my_orders/<int:order_id>', methods=['GET'])
def my_orders(order_id=None):
    if 'user_id' not in session:
        flash("Please log in to view your orders.", "danger")
        return redirect(url_for('login'))
    # Order retrieval logic follows...
```

- **Purpose**: Allows customers to view the details of their orders, which can either be a specific order or all orders.
- **Logic**:
  - **Authentication Check**: Ensures the user is logged in; if not, redirects them to the login page.
  - **Order Retrieval**: Depending on the `order_id`, retrieves either the specific order or all orders for the logged-in customer.
  - **Template Rendering**: The retrieved order details are passed to the `my_orders.html` template, which displays the information for customers to review.

### 9. **Cancel Order (Customer) Route**

```python
@app.route("/cancel_order/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    if 'user_id' not in session:
        flash("Please log in to cancel an order.", "danger")
        return redirect(url_for("login"))
    # Order cancellation logic follows...
```

- **Purpose**: Allows customers to cancel pending orders.
- **Logic**:
  - **Authentication Check**: Confirms that the user is logged in.
  - **Order Validation**: Checks that the order is in `"Pending"` status and belongs to the customer who is requesting the cancellation.
  - **Order and OrderLine Deletion**: Deletes all associated `OrderLine` records before deleting the order itself to ensure data integrity.
  - **Database Update**: Commits the changes to remove the order from the database and flashes an appropriate success or failure message.

### 10. **Customer Details Route**

```python
@app.route("/customer_details")
def customer_details():
    if 'user_id' not in session:
        flash("Please log in to view your details.", "danger")
        return redirect(url_for('login'))
    customer = Customer.query.get(session['user_id'])
    return render_template("customer_details.html", customer=customer)
```

- **Purpose**: Displays the details of the logged-in customer.
- **Logic**:
  - **Authentication Check**: Ensures the user is logged in; otherwise, redirects them to the login page.
  - **Customer Retrieval**: Retrieves the customer information using `user_id` from the session.
  - **Template Rendering**: Passes the customer details to the `customer_details.html` template for rendering, allowing users to view their own profile information.

### 11. **Update Order Status (Staff Only) Route**

```python
@app.route("/update_order_status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    if 'user_id' not in session or session['user_type'] != 'staff':
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    order = Order.query.get(order_id)
    if order:
        new_status = request.form.get("order_status")
        order.order_status = new_status
        db.session.commit()
        flash("Order status updated successfully.", "success")
    else:
        flash("Order not found.", "danger")
    return redirect(url_for("view_current_orders"))
```

- **Purpose**: Allows staff members to update the status of an order.
- **Logic**:
  - **Authentication & Authorization Check**: Ensures that the logged-in user is a staff member; otherwise, access is denied.
  - **Order Retrieval and Update**: Fetches the order by `order_id`, and if found, updates the order's status based on the form input (`order_status`).
  - **Database Update**: Commits the changes to the database and displays a success message.
  - **Redirect**: Redirects the staff member to the current orders page.

### 12. **View Current Orders Route**

```python
@app.route("/current_orders")
def view_current_orders():
    if 'user_id' not in session:
        flash("Please log in to view orders.", "danger")
        return redirect(url_for("login"))
    orders = Order.query.filter_by(order_status='Pending')
    if session['user_type'] == 'customer':
        orders = orders.filter_by(order_customer=session['user_id']).all()
    else:
        orders = orders.all()
    return render_template("current_orders.html", orders=orders)
```

- **Purpose**: Allows staff members or customers to view orders that are still pending.
- **Logic**:
  - **Authentication Check**: Verifies that the user is logged in.
  - **Order Query**: Depending on the user's role, retrieves either all pending orders (for staff) or only those orders belonging to the logged-in customer.
  - **Template Rendering**: Passes the list of pending orders to `current_orders.html` to be displayed.

### 13. **View Previous Orders (Staff and Customer Route)**

```python
@app.route("/previous_orders")
def view_previous_orders():
    if 'user_id' not in session:
        flash("Please log in to view orders.", "danger")
        return redirect(url_for("login"))
    orders = Order.query.filter(Order.order_status != 'Pending')
    if session['user_type'] == 'customer':
        orders = orders.filter_by(order_customer=session['user_id']).all()
    else:
        orders = orders.all()
    return render_template("previous_orders.html", orders=orders)
```

- **Purpose**: Displays orders that are not pending, allowing both staff and customers to review previous (completed or canceled) orders.
- **Logic**:
  - **Authentication Check**: Ensures the user is logged in before proceeding.
  - **Order Query**: Retrieves orders that are no longer in the `"Pending"` state. If the user is a customer, only their orders are fetched.
  - **Template Rendering**: The list of previous orders is passed to `previous_orders.html` for rendering.

### 14. **View All Customers (Staff Only) Route**

```python
@app.route("/customers", methods=["GET"])
def view_customers():
    if 'user_id' not in session or session['user_type'] != 'staff':
        flash("Access denied. You need to be a staff member to view this page.", "danger")
        return redirect(url_for("login"))
    # Fetch all customers logic follows...
```

- **Purpose**: Allows staff members to view all registered customers.
- **Logic**:
  - **Authentication & Authorization Check**: Ensures that the logged-in user is a staff member before proceeding.
  - **Customer Query**: Fetches all customers from the `Customer` table.
  - **Customer Type Identification**: Determines if a customer is a corporate or private customer by checking their presence in the `CorporateCustomer` table.
  - **Template Rendering**: Passes the list of customers, including their type, to `view_customers.html` for rendering.

### 15. **Generate Customer List as CSV (Staff Only) Route**

```python
@app.route("/generate_customer_list", methods=["GET"])
def generate_customer_list():
    if 'user_id' not in session or session['user_type'] != 'staff':
        flash("Access denied. You need to be a staff member to view this page.", "danger")
        return redirect(url_for("login"))
    # CSV generation logic follows...
```

- **Purpose**: Allows staff to generate a CSV file containing a list of all customers.
- **Logic**:
  - **Authentication & Authorization Check**: Ensures that the logged-in user is a staff member.
  - **Customer Query**: Fetches all customer records from the `Customer` table.
  - **CSV Generation**: Uses a generator function to yield customer data in CSV format.
  - **Response**: Returns the generated CSV as an HTTP response with appropriate headers to initiate a file download.

### 16. **Generate Sales Report (Staff Only) Route**

```python
@app.route("/generate_report", methods=["GET", "POST"])
def generate_report():
    if 'user_id' not in session or session['user_type'] != 'staff':
        flash("Access denied. You need to be a staff member to view this page.", "danger")
        return redirect(url_for("login"))
    # Report generation logic follows...
```

- **Purpose**: Allows staff members to generate sales reports based on a selected time frame (weekly, monthly, yearly).
- **Logic**:
  - **Authentication & Authorization Check**: Ensures that only staff members can access this functionality.
  - **Report Type Handling**: Determines the report type (weekly, monthly, or yearly) from the form submission.
  - **Sales Calculation**: Computes the total sales for the selected time period using the `Payment` table.
  - **Most Popular Items**: Fetches the top 5 most popular items based on the number of orders.
  - **Template Rendering**: Passes the sales data and popular items to `report.html` for rendering.

### 107. **View Most Popular Items (Staff Only) Route**

```python
@app.route("/popular_items", methods=["GET"])
def view_popular_items():
    if 'user_id' not in session or session['user_type'] != 'staff':
        flash("Access denied. You need to be a staff member to view this page.", "danger")
        return redirect(url_for("login"))
    # Popular items query logic follows...
```

- **Purpose**: Allows staff members to view the most popular items based on sales data.
- **Logic**:
  - **Authentication & Authorization Check**: Ensures that only staff members can access this route.
  - **Item Query**: Retrieves the most popular items by joining the `Item` and `OrderLine` tables and grouping by item ID.
  - **Template Rendering**: Passes the list of popular items to `popular_items.html` for rendering.


