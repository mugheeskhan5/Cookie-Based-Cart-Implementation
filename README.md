# 🛒 Cookie Shop — Shopping Cart Web App

A full-stack web application built with **Python Flask** that simulates an online cookie store with user authentication, a shopping cart, order management, and an admin dashboard.

> **Course:** Computer Networks Project  
> **Tech Stack:** Python · Flask · SQLite · HTML/CSS · JavaScript

---

## 📸 Features

| Feature | Description |
|--------|-------------|
| 🔐 Authentication | Secure signup & login with bcrypt password hashing |
| 🛍️ Shopping Cart | Add/remove items, live cart updates via JavaScript |
| 📦 Checkout | Place orders with shipping address |
| 🧾 Order History | Users can view their past orders |
| 🛡️ Admin Dashboard | Admins can view all orders and audit logs |
| 📋 Audit Logging | Every user action is recorded with timestamp |

---

## 🗂️ Project Structure

```
project/
├── app.py              # Main Flask application & all routes
├── database.py         # SQLite database setup & connection
├── models.py           # User model (Flask-Login compatible)
├── audit.py            # Action logging helper
├── update_admin.py     # Script to promote a user to admin
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css       # App styling
│   └── cart.js         # Cart logic (add/remove/update)
└── templates/
    ├── base.html            # Shared layout
    ├── index.html           # Product listing page
    ├── cart.html            # Shopping cart page
    ├── login.html           # Login page
    ├── signup.html          # Signup page
    ├── checkout_success.html
    ├── activity.html        # User order history
    └── admin_dashboard.html # Admin-only view
```

---

## ⚙️ Setup & Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/mugheeskhan5/Cookie-Based-Cart-Implementation.git
cd Cookie-Based-Cart-Implementation
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

Open your browser and go to: **http://localhost:5000**

---

## 🗄️ Database

The app uses **SQLite** and auto-creates the database on first run. No setup needed.

**Tables:**
- `users` — registered accounts with hashed passwords and roles
- `products` — pre-seeded with 6 cookie products
- `orders` — stores placed orders with cart data and shipping info
- `audit_logs` — records every login, logout, and action with timestamp

---

## 👤 Admin Access

To make a user an admin, run the script after the user has signed up:

```bash
python update_admin.py
```

Then log in with that account to access `/admin`.

---

## 🔒 Security Notes

- Passwords are hashed using **bcrypt** (never stored in plain text)
- Sessions use **HTTPOnly** and **SameSite=Strict** cookies
- All admin routes are protected with role checks
- User actions are logged in the audit table

---

## 📦 Dependencies

```
Flask==3.0.3
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
```

Install all with:
```bash
pip install -r requirements.txt
```
