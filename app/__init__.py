### Anything: tiffanyY jackieZ jessicaY claireS
### SoftDev p5
###  Oct/Nov 2024
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from build_db import setup_database

app = Flask(__name__)  # Create instance of class Flask

app.secret_key = os.urandom(24)


def get_db_connection():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    conn = get_db_connection()
    blogs = conn.execute(
        'SELECT blogs.*, users.username FROM blogs JOIN users ON blogs.user_id = users.id'
    ).fetchall()
    conn.close()
    username = session.get(
        'username')  # Get the username from the session, if available
    return render_template('home.html', username=username, blogs=blogs)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            return 'Username already exists'
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?',
                            (username, )).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/create', methods=('GET', 'POST'))
def create_blog():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        conn = get_db_connection()
        cursor = conn.cursor()  # Get the cursor from the connection
        cursor.execute(
            'INSERT INTO blogs (user_id, title, content) VALUES (?, ?, ?)',
            (session['user_id'], title, content))
        conn.commit()

        # Get the page_id of the newly created blog
        page_id = cursor.lastrowid
        conn.close()

        flash('Blog created successfully!')
        return redirect(url_for('view_blog', page_id=page_id))

    return render_template('newPage.html')


@app.route('/view_blog/<int:page_id>')
def view_blog(page_id):
    conn = get_db_connection()
    blog = conn.execute(
        '''
        SELECT blogs.*, users.username
        FROM blogs
        JOIN users ON blogs.user_id = users.id
        WHERE blogs.id = ?
    ''', (page_id, )).fetchone()
    conn.close()

    if blog is None:
        flash('Blog not found.')
        return redirect(url_for('home'))

    return render_template('blogPage.html',
                           blog=blog,
                           user_id=session.get('user_id'))


@app.route('/<int:page_id>/edit', methods=('GET', 'POST'))
def edit_blog(page_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blogs WHERE id = ? AND user_id = ?',
                        (page_id, session['user_id'])).fetchone()

    if blog is None:
        flash('Blog not found or you do not have permission to edit it.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        conn.execute('UPDATE blogs SET title = ?, content = ? WHERE id = ?',
                     (title, content, page_id))
        conn.commit()
        conn.close()

        flash('Blog updated successfully!')
        return redirect(url_for('view_blog', page_id=page_id))

    conn.close()
    return render_template('editPage.html', blog=blog)


@app.route('/users')
def list_users():
    if 'user_id' not in session:
        flash("You must be logged in to view the users list.")
        return redirect(url_for('login'))

    # Fetch and display the users if logged in
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('users.html', users=users)


@app.route('/pages/<int:user_id>')
def user_pages(user_id):
    if 'user_id' not in session:
        flash("You must be logged in to view user pages.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    pages = conn.execute('SELECT * FROM blogs WHERE user_id = ?',
                         (user_id, )).fetchall()
    conn.close()
    return render_template('user_pages.html', pages=pages)


@app.route('/mypages')
def my_pages():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    pages = conn.execute('SELECT * FROM blogs WHERE user_id = ?',
                         (session['user_id'], )).fetchall()
    conn.close()

    return render_template('my_pages.html', pages=pages)


if __name__ == "__main__":
    app.debug = True
    app.run()
