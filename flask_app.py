from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from helpers import UserException
from user_db import (
    add_hobby,
    add_user,
    check_user_password,
    get_hobbies,
    get_user,
    init_db,
    remove_hobby,
)

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session handling

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
init_db(app)


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/home")
def home():
    if "user" in session:
        user = get_user(session["user"])
        hobbies = get_hobbies(user.id)
        return render_template("home.html", user=user, hobbies=hobbies)
    return redirect(url_for("landing"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            user = get_user(username)
            if user and check_user_password(user, password):
                session["user"] = username
                return redirect(url_for("home"))
            raise UserException("Invalid username or password! Try again.")
        except UserException as e:
            return render_template("login.html", message=str(e))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("landing"))


@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            add_user(username, password)
            return redirect(url_for("login"))
        return render_template("register.html")
    except UserException as e:
        return render_template("register.html", message=str(e))


@app.route("/add_hobby", methods=["POST"])
def add_hobby_route():
    if "user" in session:
        user = get_user(session["user"])
        hobby_name = request.json["hobby"]
        try:
            new_hobby = add_hobby(user.id, hobby_name)
            return jsonify(success=True, hobby_id=new_hobby.id)
        except UserException as e:
            return jsonify(success=False, message=str(e))
    return jsonify(success=False)


@app.route("/remove_hobby/<int:hobby_id>")
def remove_hobby_route(hobby_id):
    if "user" in session:
        remove_hobby(hobby_id)
        return redirect(url_for("home"))
    return redirect(url_for("landing"))


if __name__ == "__main__":
    app.run(debug=True)
