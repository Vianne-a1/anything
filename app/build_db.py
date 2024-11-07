   ### Anything: tiffanyY jackieZ jessicaY claireS
   ### SoftDev p5
  ###  Oct/Nov 2024


import sqlite3

def setup_database():
    conn = sqlite3.connect('blog.db')
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    conn.close()

if __name__ == "__main__":
    setup_database()