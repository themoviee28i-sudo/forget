import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'bakery_shop_secret_key_2026'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configuration
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database initialization
DATABASE = 'bakery.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            payment_method TEXT NOT NULL,
            items TEXT NOT NULL,
            customer_name TEXT,
            customer_email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database on app start
with app.app_context():
    init_db()

# ==================== ADMIN ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded credentials
        if username == 'admin' and password == '1234':
            session['user'] = 'admin'
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('index'))

def login_required(f):
    """Decorator to protect admin routes"""
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard - display all products"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image = request.files.get('image')
        
        # Validation
        if not name or not price:
            return render_template('add_product.html', error='Name and price are required')
        
        try:
            price = float(price)
        except ValueError:
            return render_template('add_product.html', error='Price must be a number')
        
        image_filename = None
        if image and image.filename != '':
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                # Add timestamp to make filename unique
                import time
                filename = f"{int(time.time())}_{filename}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            else:
                return render_template('add_product.html', error='Invalid file type. Allowed: png, jpg, jpeg, gif')
        
        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, price, image) VALUES (?, ?, ?)',
                      (name, price, image_filename))
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_product.html')

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit product"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image = request.files.get('image')
        
        # Validation
        if not name or not price:
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            product = cursor.fetchone()
            conn.close()
            return render_template('edit_product.html', product=product, error='Name and price are required')
        
        try:
            price = float(price)
        except ValueError:
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            product = cursor.fetchone()
            conn.close()
            return render_template('edit_product.html', product=product, error='Price must be a number')
        
        # Get current product
        cursor.execute('SELECT image FROM products WHERE id = ?', (product_id,))
        current_product = cursor.fetchone()
        image_filename = current_product['image']
        
        # Handle new image upload
        if image and image.filename != '':
            if allowed_file(image.filename):
                # Delete old image if exists
                if image_filename and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], image_filename)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                
                # Save new image
                filename = secure_filename(image.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            else:
                cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
                product = cursor.fetchone()
                conn.close()
                return render_template('edit_product.html', product=product, error='Invalid file type')
        
        # Update database
        cursor.execute('UPDATE products SET name = ?, price = ?, image = ? WHERE id = ?',
                      (name, price, image_filename, product_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    
    # GET request
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return redirect(url_for('dashboard'))
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get image filename before deleting
    cursor.execute('SELECT image FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    
    if product and product['image']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Delete from database
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard'))

# ==================== CUSTOMER ROUTES ====================

@app.route('/')
def index():
    """Homepage - display all products"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    """Add product to cart (session-based)"""
    if 'cart' not in session:
        session['cart'] = {}
    
    # Get product details
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return redirect(url_for('index'))
    
    # Add to cart or increment quantity
    product_id_str = str(product_id)
    if product_id_str in session['cart']:
        session['cart'][product_id_str]['quantity'] += 1
    else:
        session['cart'][product_id_str] = {
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'image': product['image'],
            'quantity': 1
        }
    
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    """View shopping cart"""
    cart_items = session.get('cart', {})
    total = 0
    
    for item in cart_items.values():
        total += item['price'] * item['quantity']
    
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    """Remove item from cart"""
    if 'cart' in session:
        product_id_str = str(product_id)
        if product_id_str in session['cart']:
            del session['cart'][product_id_str]
            session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart quantities"""
    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    
    if 'cart' in session and product_id in session['cart']:
        if quantity <= 0:
            del session['cart'][product_id]
        else:
            session['cart'][product_id]['quantity'] = quantity
        session.modified = True
    
    return jsonify({'success': True})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page"""
    cart_items = session.get('cart', {})
    
    if not cart_items:
        return redirect(url_for('cart'))
    
    total = 0
    for item in cart_items.values():
        total += item['price'] * item['quantity']
    
    if request.method == 'POST':
        customer_name = request.form.get('name')
        customer_email = request.form.get('email')
        payment_method = request.form.get('payment_method')
        
        # Validation
        if not customer_name or not customer_email or not payment_method:
            return render_template('checkout.html', cart=cart_items, total=total, 
                                 error='All fields are required')
        
        # Prepare order items text
        order_items = ', '.join([f"{item['name']} x{item['quantity']}" for item in cart_items.values()])
        
        # Save order to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO orders (total, payment_method, items, customer_name, customer_email)
                         VALUES (?, ?, ?, ?, ?)''',
                      (total, payment_method, order_items, customer_name, customer_email))
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        
        # Clear cart
        session['cart'] = {}
        session.modified = True
        
        return render_template('success.html', order_id=order_id, total=total, 
                             payment_method=payment_method)
    
    return render_template('checkout.html', cart=cart_items, total=total)

@app.route('/orders')
@login_required
def orders():
    """View all orders (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
    all_orders = cursor.fetchall()
    conn.close()
    return render_template('orders.html', orders=all_orders)

# ==================== ERROR HANDLING ====================

@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
