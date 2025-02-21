from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from user_db import db, init_db, add_user, get_user, check_user_password, add_hobby, remove_hobby, get_hobbies
from helpers import UserException

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
        user = get_user(session['user'])
        hobbies = get_hobbies(user.id)
        return render_template("home.html", user=user, hobbies=hobbies)
    return redirect(url_for('landing'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            user = get_user(username)
            if user and check_user_password(user, password):
                session['user'] = username
                return redirect(url_for('home'))
            raise UserException("Invalid username or password! Try again.")
        except UserException as e:
            return render_template("login.html", message=str(e))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('landing'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            

            add_user(username, password)
            return redirect(url_for('login'))
        else:
            return render_template("register.html")
    except UserException as e:
        return render_template("register.html", message=str(e))

@app.route('/add_hobby', methods=['POST'])
def add_hobby_route():
    if "user" in session:
        user = get_user(session['user'])
        hobby_name = request.json['hobby']
        new_hobby = add_hobby(user.id, hobby_name)
        return jsonify(success=True, hobby_id=new_hobby.id)
    return jsonify(success=False)

@app.route('/remove_hobby/<int:hobby_id>')
def remove_hobby_route(hobby_id):
    if "user" in session:
        remove_hobby(hobby_id)
        return redirect(url_for('home'))
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)