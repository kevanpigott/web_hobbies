from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from helpers import UserException
from user_db import DbManager

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session handling

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DbManager.FILE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
DbManager.init_db(app)

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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

@login_manager.user_loader
def load_user(user_id):
    return DbManager.get_user_by_id(user_id)


@app.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("landing.html")


@app.route("/home")
@login_required
def home():
    hobbies = DbManager.get_user_hobbies(current_user.id)
    return render_template("home.html", user=current_user, hobbies=hobbies)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            user = DbManager.get_user(username)
            if user and DbManager.check_user_password(user, password):
                login_user(user)
                return redirect(url_for("home"))
            raise UserException("Invalid username or password! Try again.")
        except UserException as e:
            return render_template("login.html", message=str(e))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
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
@login_required
def add_hobby_route():
    hobby_name = request.json["hobby"]
    try:
        new_hobby = DbManager.add_hobby_to_user(current_user.id, hobby_name)
        return jsonify(success=True, hobby_id=new_hobby.id)
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/remove_hobby/<int:hobby_id>")
@login_required
def remove_hobby_route(hobby_id):
    DbManager.remove_hobby_from_user(current_user.id, hobby_id)
    return redirect(url_for("home"))


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
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for("home"))

    user = DbManager.get_user(username)
    hobbies = DbManager.get_user_hobbies(user.id)
    return render_template("user.html", user=user, hobbies=hobbies)


@app.route("/recount_hobbies")
@login_required
def recount_hobbies():
    DbManager.recount_hobbies()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
