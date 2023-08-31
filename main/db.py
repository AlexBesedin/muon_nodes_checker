import sqlite3

def create_database():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (user_id INTEGER PRIMARY KEY, 
                          interaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                       '''
                       )
        conn.commit()
