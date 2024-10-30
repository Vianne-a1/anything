from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from build_db import setup_database
app.secret_key = os.random(64)
def get_db_connection():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
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
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
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
        cursor = conn.execute('INSERT INTO blogs (user_id, title, content) VALUES (?, ?, ?)',
                              (session['user_id'], title, content))
        conn.commit()
        
        # Get the page_id of the newly created blog
        page_id = cursor.lastrowid
        conn.close()
        
        flash('Blog created successfully!')
        return redirect(url_for('view_blog', page_id=page_id))
    
    return render_template('newPage.html')

@app.route('/page/<int:page_id>')
def view_blog(page_id):
    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blogs WHERE id = ?', (page_id,)).fetchone()
    conn.close()
    
    if blog is None:
        flash('Blog not found.')
        return redirect(url_for('home'))
    
    return render_template('blogPage.html', blog=blog)

@app.route('/<int:page_id>/edit', methods=('GET', 'POST'))
def edit_blog(page_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blogs WHERE id = ? AND user_id = ?', (page_id, session['user_id'])).fetchone()
    
    if blog is None:
        flash('Blog not found or you do not have permission to edit it.')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        conn.execute('UPDATE blogs SET title = ?, content = ? WHERE id = ?', (title, content, page_id))
        conn.commit()
        conn.close()
        
        flash('Blog updated successfully!')
        return redirect(url_for('view_blog', page_id=page_id))
    
    conn.close()
    return render_template('editPage.html', blog=blog)
