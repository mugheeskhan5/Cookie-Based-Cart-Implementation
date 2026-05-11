import sqlite3
from flask import g

DATABASE = 'shopping_cart.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_connection)
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create audit_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                shipping_address TEXT,
                cart_data TEXT,
                total_price REAL,
                status TEXT DEFAULT 'Pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        ''')
        
        # Seed products if empty
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            default_products = [
                ("p1", "Classic Chocolate Chip", 2.99, "Our signature cookie, loaded with semi-sweet chocolate chips."),
                ("p2", "Double Dark Chocolate", 3.49, "Rich dark chocolate cookie with dark chocolate chunks."),
                ("p3", "Oatmeal Raisin", 2.79, "Chewy oatmeal cookie baked with plump raisins and cinnamon."),
                ("p4", "Peanut Butter Blast", 3.29, "Creamy peanut butter dough topped with peanut butter chips."),
                ("p5", "Snickerdoodle", 2.89, "Soft sugar cookie rolled in a sweet cinnamon-sugar blend."),
                ("p6", "White Macadamia Nut", 3.99, "Premium cookie with white chocolate chunks and roasted macadamia nuts.")
            ]
            cursor.executemany("INSERT INTO products (id, name, price, description) VALUES (?, ?, ?, ?)", default_products)
        
        db.commit()
