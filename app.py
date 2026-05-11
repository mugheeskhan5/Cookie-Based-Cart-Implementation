import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

from database import init_db, get_db
from models import User
from audit import log_action

app = Flask(__name__)
app.secret_key = os.urandom(24) # Ensure session is secure

# Initialize extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."

# Secure session cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False # Set to False for local testing without HTTPS, else session cookie won't be set!
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Initialize DB on startup
init_db(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return render_template('index.html', products=products)

@app.route('/cart')
def cart():
    # Cart display logic is handled via client-side JS reading cookies
    return render_template('cart.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.find_by_username(username)
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            log_action(user.id, user.username, "User logged in")
            flash("Logged in successfully.", "success")
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
                
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("Username already exists.", "error")
        else:
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            role = 'admin' if username.lower() == 'admin' else 'user'
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
            db.commit()
            
            # log action
            new_user = User.find_by_username(username)
            log_action(new_user.id, username, "User signed up")
            
            flash("Account created! You can now log in.", "success")
            return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    log_action(current_user.id, current_user.username, "User logged out")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/activity')
@login_required
def activity():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT timestamp, action, details 
        FROM audit_logs 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''', (current_user.id,))
    logs = cursor.fetchall()
    return render_template('activity.html', logs=logs)

@app.route('/log-action', methods=['POST'])
def api_log_action():
    data = request.get_json()
    action = data.get('action')
    details = data.get('details', '')
    
    if current_user.is_authenticated:
        log_action(current_user.id, current_user.username, action, details)
    else:
        log_action(None, "guest", action, details)
        
    return jsonify({"status": "success"}), 200

@app.route('/checkout', methods=['POST'])
def checkout():
    shipping_address = request.form.get('shipping_address')
    cart_data_str = request.form.get('cart_data')
    
    if not cart_data_str or cart_data_str == '[]':
        flash("Your cart is empty.", "error")
        return redirect(url_for('cart'))
        
    if not shipping_address:
        flash("Shipping address is required.", "error")
        return redirect(url_for('cart'))
        
    try:
        cart_data = json.loads(cart_data_str)
        total_price = sum(item['p'] * item['q'] for item in cart_data)
    except Exception as e:
        flash("Invalid cart data.", "error")
        return redirect(url_for('cart'))
        
    db = get_db()
    cursor = db.cursor()
    user_id = current_user.id if current_user.is_authenticated else None
    
    cursor.execute('''
        INSERT INTO orders (user_id, shipping_address, cart_data, total_price)
        VALUES (?, ?, ?, ?)
    ''', (user_id, shipping_address, cart_data_str, total_price))
    db.commit()
    
    if current_user.is_authenticated:
        log_action(current_user.id, current_user.username, "Order placed", f"Total: ${total_price:.2f}")
    else:
        log_action(None, "guest", "Order placed", f"Total: ${total_price:.2f}")
        
    # Instruct frontend to clear cart via a flash message or template variable if we wanted, 
    # but instead we will render a success page that includes JS to clear the cookie.
    flash("Your order has been placed successfully!", "success")
    return render_template('checkout_success.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('index'))
        
    db = get_db()
    cursor = db.cursor()
    
    # Fetch orders
    cursor.execute('''
        SELECT o.id, o.shipping_address, o.cart_data, o.total_price, o.status, o.created_at, u.username
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    ''')
    orders = cursor.fetchall()
    
    parsed_orders = []
    for order in orders:
        order_dict = dict(order)
        order_dict['cart_items'] = json.loads(order_dict['cart_data'])
        parsed_orders.append(order_dict)
        
    # Fetch products
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
        
    return render_template('admin_dashboard.html', orders=parsed_orders, products=products)

@app.route('/admin/orders/update-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
        
    new_status = request.form.get('status')
    if new_status in ['Pending', 'Shipped', 'Delivered']:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
        db.commit()
        log_action(current_user.id, current_user.username, "Order status updated", f"Order #{order_id} -> {new_status}")
        flash(f"Order #{order_id} marked as {new_status}.", "success")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/products/add', methods=['POST'])
@login_required
def add_product():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
        
    pid = request.form.get('id')
    name = request.form.get('name')
    price = request.form.get('price')
    desc = request.form.get('description')
    
    if pid and name and price:
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO products (id, name, price, description) VALUES (?, ?, ?, ?)', (pid, name, float(price), desc))
            db.commit()
            log_action(current_user.id, current_user.username, "Product added", f"{name}")
            flash(f"Product '{name}' added successfully.", "success")
        except Exception as e:
            flash(f"Error adding product: {str(e)}", "error")
            
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/products/remove/<string:product_id>', methods=['POST'])
@login_required
def remove_product(product_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    db.commit()
    log_action(current_user.id, current_user.username, "Product removed", f"ID: {product_id}")
    flash("Product removed successfully.", "success")
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
