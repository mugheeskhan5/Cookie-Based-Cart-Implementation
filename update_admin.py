import sqlite3
db = sqlite3.connect(r'c:\Users\User\Desktop\CN PROJECT\shopping_cart.db')
db.execute("UPDATE users SET role='admin' WHERE username='admin'")
db.commit()
db.close()
print("Updated admin role successfully.")
