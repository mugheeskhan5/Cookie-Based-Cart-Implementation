from flask_login import UserMixin
from database import get_db

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

    @staticmethod
    def get(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return User(id=row['id'], username=row['username'], password=row['password'], role=row['role'])

    @staticmethod
    def find_by_username(username):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return None
        return User(id=row['id'], username=row['username'], password=row['password'], role=row['role'])
