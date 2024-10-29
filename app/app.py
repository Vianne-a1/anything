from flask import Flask            
from flask import render_template   
from flask import request
app = Flask(__name__)
@app.route('/')
def home():
    return render_template( 'home.html')
@app.route('/login', methods=['POST'])
def index():
    username = request.cookies.get('username')
    if username:
        return render_template('response.html', username=username, request="Already Logged In")
    return render_template('login.html')
    