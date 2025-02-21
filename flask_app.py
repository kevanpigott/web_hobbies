from flask import Flask, render_template, request, redirect, url_for, session
from user_db import db, init_db, add_user, get_user, check_user_password

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session handling

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
init_db(app)

@app.route('/')
def landing():
    return render_template("landing.html")

@app.route('/home')
def home():
    if "user" in session:
        return render_template("home.html", user=session['user'])
    return redirect(url_for('landing'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user(username)
        if user and check_user_password(user, password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid credentials! Try again."
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('landing'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user(username)
        if user:
            return "Username already exists! Try again."
        else:
            if add_user(username, password): # redundancy check
                session['user'] = username
                return redirect(url_for('home'))
    return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True)