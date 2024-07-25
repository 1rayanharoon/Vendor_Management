from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

MONGO_URI = "mongodb+srv://ibtsamsohail:mongo12345@cluster0.irr8qij.mongodb.net/?retryWrites=true&w=majority"


try:
    client = MongoClient(MONGO_URI)
    db = client.VendorManagement  
    users_collection = db.users  
    print("Connected to MongoDB!")
except ConnectionFailure as e:
    print(f"Error while connecting to MongoDB: {e}")

@app.route('/')
def index():
    # Redirect to login if not authenticated
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the submitted credentials
        username = request.form['username']
        password = request.form['password']
    
        user = users_collection.find_one({"username": username, "password": password})
        if user:    
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        if request.method == 'POST':
            # Handle POST request here, for example, updating user settings or processing form data
            pass
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
