from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from helpers import UserException
from user_db import DbManager

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session handling

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DbManager.FILE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
DbManager.init_db(app)

"""
from flask_session import Session
import redis
# Configure server-side session storage
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = redis.StrictRedis(host="localhost", port=6379)

# Initialize the session
Session(app)
"""


@app.route("/")
def landing():
    if "user" in session:
        return redirect(url_for("home"))
    return render_template("landing.html")


@app.route("/home")
def home():
    if "user" in session:
        user = DbManager.get_user(session["user"])
        hobbies = DbManager.get_user_hobbies(user.id)
        return render_template("home.html", user=user, hobbies=hobbies)
    return redirect(url_for("landing"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            user = DbManager.get_user(username)
            if user and DbManager.check_user_password(user, password):
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
            DbManager.add_user(username, password)
            return redirect(url_for("login"))
        return render_template("register.html")
    except UserException as e:
        return render_template("register.html", message=str(e))


@app.route("/add_hobby", methods=["POST"])
def add_hobby_route():
    if "user" in session:
        user = DbManager.get_user(session["user"])
        hobby_name = request.json["hobby"]
        try:
            new_hobby = DbManager.add_hobby_to_user(user.id, hobby_name)
            return jsonify(success=True, hobby_id=new_hobby.id)
        except UserException as e:
            return jsonify(success=False, message=str(e))
    return jsonify(success=False)


@app.route("/remove_hobby/<int:hobby_id>")
def remove_hobby_route(hobby_id):
    if "user" in session:
        user = DbManager.get_user(session["user"])
        DbManager.remove_hobby_from_user(user.id, hobby_id)
        return redirect(url_for("home"))
    return redirect(url_for("landing"))


@app.route("/popular_hobbies", methods=["GET"])
def popular_hobbies():
    page = int(request.args.get("page", 1))
    per_page = 5
    offset = (page - 1) * per_page

    hobbies = DbManager.get_most_popular_hobbies(limit=per_page, offset=offset)

    return jsonify(
        hobbies=[
            {"name": hobby.name, "user_count": hobby.user_count, "id": hobby.id} for hobby in hobbies
        ],
        total_pages=DbManager.number_of_hobbies() // per_page + 1,
        start=str(offset + 1),
    )


@app.route("/hobby/<int:hobby_id>")
def hobby(hobby_id):
    hobby = DbManager.get_hobby(hobby_id)
    users = DbManager.get_users_by_hobby(hobby_id)
    return render_template("hobby.html", hobby=hobby, users=users)


@app.route("/user/<string:username>")
def user(username):
    if "user" in session:
        current_user = DbManager.get_user(session["user"])
        if current_user.username == username:
            return redirect(url_for("home"))

    user = DbManager.get_user(username)
    hobbies = DbManager.get_user_hobbies(user.id)
    return render_template("user.html", user=user, hobbies=hobbies)


@app.route("/recount_hobbies")
def recount_hobbies():
    DbManager.recount_hobbies()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
