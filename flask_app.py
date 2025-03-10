import logging
from datetime import datetime
from math import ceil

import pytz
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from helpers import UserException
from user_db import DbManager, User

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)


# Log each request
@app.before_request
def log_request_info():
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    referrer = request.referrer
    user = current_user.username if current_user.is_authenticated else "Anonymous"
    timestamp = datetime.now().isoformat()
    logging.info(
        f"Request from {ip} by {user} at {timestamp}: {request.method} {request.url} - "
        f"User-Agent: {user_agent} - Referrer: {referrer} - Data: {request.get_data()}"
    )


# Log each response
@app.after_request
def log_response_info(response):
    ip = request.remote_addr
    user = current_user.username if current_user.is_authenticated else "Anonymous"
    try:
        response_data = response.get_data()
    except RuntimeError:
        response_data = b""
    logging.info(f"Response to {ip} by {user}: {response.status} - Data: {response_data}")
    return response


@login_manager.user_loader
def load_user(user_id) -> User:
    """
    Load a user by their user ID.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User: The user object.
    """
    return DbManager.get_user_by_id(user_id)


@app.route("/")
def landing():
    """
    Render the landing page. Redirect to the home page if the user is authenticated.

    Returns:
        Response: The rendered landing page or a redirect to the home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("landing.html")


@app.route("/home")
@login_required
def home():
    """
    Render the home page. This route requires the user to be logged in.

    Returns:
        Response: The rendered home page.
    """
    return render_template("home.html")


@app.route("/get_current_user", methods=["GET"])
@login_required
def get_current_user():
    """
    Get the current authenticated user.

    Returns:
        Response: A JSON response with the current user's information.
    """
    if current_user.is_authenticated:
        return jsonify(success=True, user={"id": current_user.id, "username": current_user.username})
    return jsonify(success=False, user="")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login. Render the login page on GET requests and process login on POST requests.

    Returns:
        Response: The rendered login page or a redirect to the home page.
    """
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            user = DbManager.get_user(username)
            if user and DbManager.check_user_password(user, password):
                login_user(user)
                logging.info(f"User {username} logged in from {request.remote_addr} at {datetime.now()}")
                return redirect(url_for("home"))
            raise UserException("Invalid username or password! Try again.")
        except UserException as e:
            return render_template("login.html", message=str(e))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """
    Log out the current user and redirect to the landing page.

    Returns:
        Response: A redirect to the landing page.
    """
    logout_user()
    return redirect(url_for("landing"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration. Render the registration page on GET requests and process
    registration on POST requests.

    Returns:
        Response: The rendered registration page or a redirect to the login page.
    """
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            DbManager.add_user(username, password)
            return redirect(url_for("login"))
        return render_template("register.html")
    except UserException as e:
        return render_template("register.html", message=str(e))


@app.route("/add_hobby/<string:hobby_name>", methods=["POST"])
@login_required
def add_hobby_route(hobby_name):
    """
    Add a hobby to the current user's list of hobbies.

    Args:
        hobby_name (str): The name of the hobby to add.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    try:
        new_hobby = DbManager.add_hobby_to_user(current_user.id, hobby_name)
        return jsonify(success=True, hobby_id=new_hobby.id)
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/remove_hobby/<int:hobby_id>", methods=["DELETE"])
@login_required
def remove_hobby_route(hobby_id):
    """
    Remove a hobby from the current user's list of hobbies.

    Args:
        hobby_id (int): The ID of the hobby to remove.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    try:
        DbManager.remove_hobby_from_user(current_user.id, hobby_id)
        return jsonify(success=True)
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/popular_hobbies/<int:page_num>", methods=["GET"])
def popular_hobbies(page_num):
    """
    Get a list of the most popular hobbies, paginated.

    Args:
        page_num (int): The page number to retrieve.

    Returns:
        Response: A JSON response with the list of popular hobbies.
    """

    page = int(page_num)
    per_page = 5
    offset = (page - 1) * per_page

    hobbies = DbManager.get_most_popular_hobbies(limit=per_page, offset=offset)

    return jsonify(
        hobbies=[
            {"name": hobby.name, "user_count": hobby.user_count, "id": hobby.id} for hobby in hobbies
        ],
        total_pages=ceil(DbManager.number_of_hobbies() / per_page),
        start=str(offset + 1),
    )


@app.route("/hobby/<int:hobby_id>")
def hobby(hobby_id):
    """
    Get details about a specific hobby and the users who have it.

    Args:
        hobby_id (int): The ID of the hobby to retrieve.

    Returns:
        Response: The rendered hobby details page.
    """

    hobby = DbManager.get_hobby(hobby_id)
    users = DbManager.get_users_by_hobby(hobby_id)
    return render_template("hobby.html", hobby=hobby, users=users)


@app.route("/user/<string:username>")
def user(username):
    """
    Get details about a specific user and their hobbies.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        Response: The rendered user profile page.
    """
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for("home"))

    user = DbManager.get_user(username)
    hobbies = DbManager.get_user_hobbies(user.id)
    return render_template("user.html", user=user, hobbies=hobbies)


@app.route("/get_user_hobbies/<int:user_id>", methods=["GET"])
def get_user_hobbies(user_id):
    """
    Get a list of hobbies for a specific user.

    Args:
        user_id (int): The ID of the user to retrieve hobbies for.

    Returns:
        Response: A JSON response with the list of hobbies.
    """
    try:
        user = DbManager.get_user_by_id(user_id)
        hobbies = DbManager.get_user_hobbies(user.id)
        return jsonify(success=True, hobbies=[{"name": hobby.name, "id": hobby.id} for hobby in hobbies])
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/most_common_user", methods=["GET"])
@login_required
def most_common_user():
    """
    Get the user with the most common hobbies.

    Returns:
        Response: A JSON response with the most common user's information.
    """
    try:
        most_common_user = DbManager.get_most_common_user(current_user.id)
        return jsonify(
            success=True, user={"id": most_common_user.id, "username": most_common_user.username}
        )
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/most_common_user_never_met", methods=["GET"])
@login_required
def most_common_user_never_met():
    """
    Get the user with the most common hobbies that the current user has never met.

    Returns:
        Response: A JSON response with the most common user's information.
    """
    try:
        most_common_user = DbManager.get_most_common_user_never_met(current_user.id)
        return jsonify(
            success=True, user={"id": most_common_user.id, "username": most_common_user.username}
        )
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/schedule_one_on_one/<int:user_id>/<string:datetime_str>", methods=["POST"])
@login_required
def schedule_one_on_one(user_id, datetime_str):
    """
    Schedule a one-on-one meeting with another user.

    Args:
        user_id (int): The ID of the user to schedule the meeting with.
        datetime_str (str): The date and time of the meeting

    Returns:
        Response: A JSON response indicating success or failure.
    """
    try:
        # Convert string to datetime object in UTC
        utc_time = datetime.fromisoformat(datetime_str).replace(tzinfo=pytz.UTC)

        # Make sure the meeting is in the future
        if utc_time < datetime.now(pytz.UTC):
            raise UserException("Meeting must be scheduled in the future.")

        # Schedule the one-on-one meeting
        DbManager.add_one_on_one(current_user.id, user_id, utc_time)
        return jsonify(success=True)
    except ValueError:
        return jsonify(success=False, message="Invalid date and time format. Use 'YYYY-MM-DD-HH-MM'.")
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/cancel_one_on_one/<int:one_on_one_id>", methods=["DELETE"])
@login_required
def cancel_one_on_one(one_on_one_id):
    """
    Cancel a one-on-one meeting with another user.

    Args:
        one_on_one_id (int): The ID of the one-on-one meeting to cancel.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    try:
        # check if user is part of the one-on-one meeting
        one_on_one = DbManager.get_one_on_one(one_on_one_id)
        if current_user.id != one_on_one.user_id1 and current_user.id != one_on_one.user_id2:
            raise UserException("You are not part of this one-on-one meeting.")

        DbManager.cancel_one_on_one(one_on_one_id)
        return jsonify(success=True)
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/get_user_one_on_ones/<int:user_id>", methods=["GET"])
@login_required
def get_user_one_on_ones(user_id):
    """
    Get a list of users that the current user has one-on-one hobbies with.

    Args:
        user_id (int): The ID of the user to retrieve one-on-one hobbies for.

    Returns:
        Response: A JSON response with the list of one-on-one hobbies.
    """
    try:
        user = DbManager.get_user_by_id(user_id)
        one_on_ones = DbManager.get_user_one_on_ones(user.id)

        ret = []
        for one_on_one in one_on_ones:
            meeting_partner = DbManager.get_user_by_id(
                one_on_one.user_id1 if one_on_one.user_id1 != current_user.id else one_on_one.user_id2
            )
            ret.append({
                "date": str(one_on_one.date),
                "user": {"username": meeting_partner.username, "id": meeting_partner.id},
                "id": one_on_one.id,
            })
        return jsonify(success=True, one_on_ones=ret)
    except UserException as e:
        return jsonify(success=False, message=str(e))


@app.route("/recount_hobbies")
@login_required
def recount_hobbies():
    """
    Recount hobby participants for all hobbies.

    Returns:
        Response: A redirect to the home page.
    """
    DbManager.recount_hobbies()
    return redirect(url_for("home"))


# track redirects
@app.route("/redirect/github")
def redirect_github():
    return redirect("https://github.com/kevanpigott/")


@app.route("/redirect/github_web_hobbies")
def redirect_github_web_hobbies():
    return redirect("https://github.com/kevanpigott/web_hobbies")


@app.route("/redirect/linkedin")
def redirect_linkedin():
    return redirect("https://www.linkedin.com/in/kevan-pigott/")


if __name__ == "__main__":
    app.run(debug=True)
