from database import get_db

def log_action(user_id, username, action, details=None):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (user_id, username, action, details) VALUES (?, ?, ?, ?)",
        (user_id, username, action, details)
    )
    db.commit()
