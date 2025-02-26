import bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from helpers import UserException

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Master table for users, one record per user"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)


class Hobby(db.Model):
    """Master table for Hobbies, one record per user"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    user_count = db.Column(db.Integer, nullable=False, default=0)


class UserHobby(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    hobby_id = db.Column(db.Integer, db.ForeignKey("hobby.id"), primary_key=True)


class HobbyRelation(db.Model):
    hobby_id1 = db.Column(db.Integer, db.ForeignKey("hobby.id"), primary_key=True)
    hobby_id2 = db.Column(db.Integer, db.ForeignKey("hobby.id"), primary_key=True)
    similarity = db.Column(db.Float, nullable=False)


class DbManager:
    FILE_NAME = "tables.db"

    @classmethod
    def init_db(cls, app) -> None:
        """Initialize the database with the given Flask app."""
        db.init_app(app)
        with app.app_context():
            db.create_all()

    @classmethod
    def get_user(cls, username: str) -> User:
        """Given a username, return the user object."""
        return User.query.filter_by(username=username).first()

    @classmethod
    def get_user_by_id(cls, user_id: int) -> User:
        """Given a user_id, return the user object."""
        return User.query.get(user_id)

    @classmethod
    def add_user(cls, username: str, password: str) -> None:
        """Given user details, add a new user."""
        if cls.get_user(username):
            raise UserException("Username already exists! Try again.")

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        new_user = User(
            username=username,
            password=hashed_password.decode("utf-8"),
            email=f"{username}@fake_email.com",
        )
        db.session.add(new_user)
        db.session.commit()

    @classmethod
    def check_user_password(cls, user: User, password: str) -> bool:
        """Given a user object and a password, check if the password is correct."""
        return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))

    @classmethod
    def calculate_all_relations_for_hobby(cls, hobby: Hobby) -> None:
        """Calculate all relations for a given hobby."""
        # TODO: Implement this function

    @classmethod
    def add_hobby_to_user(cls, user_id: int, hobby_name: str) -> Hobby:
        """Given a user and a hobby, create a new Hobby if it does not exist,
        link the user to the hobby in the UserHobby table.
        """
        hobby_name = hobby_name.strip().lower()
        if not hobby_name:
            raise UserException("Hobby name cannot be empty!")

        # Check if User exists
        user = User.query.get(user_id)
        if not user:
            raise UserException("User does not exist!")

        # Check if Hobby exists
        existing_hobby = Hobby.query.filter_by(name=hobby_name).first()
        if not existing_hobby:
            existing_hobby = Hobby(name=hobby_name)
            db.session.add(existing_hobby)
            db.session.commit()
            cls.calculate_all_relations_for_hobby(existing_hobby)

        # Ensure the hobby has a valid ID
        if existing_hobby.id is None:
            raise UserException("Failed to add hobby to the database!")

        # Check if UserHobby already exists
        existing_user_hobby = UserHobby.query.filter_by(
            user_id=user_id, hobby_id=existing_hobby.id
        ).first()
        if existing_user_hobby:
            raise UserException("Hobby already exists for this user!")

        existing_hobby.user_count += 1
        new_user_hobby = UserHobby(user_id=user_id, hobby_id=existing_hobby.id)
        db.session.add(new_user_hobby)
        db.session.commit()

        return existing_hobby

    @classmethod
    def remove_hobby_from_user(cls, user_id: int, hobby_id: int) -> None:
        """Given a user and a hobby, remove the hobby from the user."""
        hobby = Hobby.query.filter_by(id=hobby_id).first()
        if not hobby:
            raise UserException("Hobby does not exist!")
        user_hobby = UserHobby.query.filter_by(user_id=user_id, hobby_id=hobby.id).first()
        if not user_hobby:
            raise UserException("User does not have this hobby!")

        hobby = Hobby.query.get(hobby.id)
        hobby.user_count -= 1
        db.session.delete(user_hobby)
        db.session.commit()

    @classmethod
    def get_user_hobbies(cls, user_id: int) -> list[Hobby]:
        """Given a user, return a list of hobbies."""
        user_hobbies = UserHobby.query.filter_by(user_id=user_id).all()
        # Get the hobby names
        return [Hobby.query.get(user_hobby.hobby_id) for user_hobby in user_hobbies]

    @classmethod
    def number_of_hobbies(cls):
        """Return the total number of hobbies."""
        return Hobby.query.count()

    @classmethod
    def get_most_popular_hobbies(cls, limit=15, offset=0):
        """Return a list of the most popular hobbies."""
        return Hobby.query.order_by(Hobby.user_count.desc()).limit(limit).offset(offset).all()

    @classmethod
    def recount_hobbies(cls):
        """Recount the number of users for each hobby."""
        hobbies = Hobby.query.all()
        for hobby in hobbies:
            hobby.user_count = UserHobby.query.filter_by(hobby_id=hobby.id).count()
        db.session.commit()

    @classmethod
    def get_hobby(cls, hobby_id: int) -> Hobby:
        """Return a hobby by its ID."""
        return Hobby.query.get(hobby_id)

    @classmethod
    def get_users_by_hobby(cls, hobby_id: int) -> list[User]:
        """Return a list of users who have a specific hobby."""
        user_hobbies = UserHobby.query.filter_by(hobby_id=hobby_id).all()
        return [User.query.get(user_hobby.user_id) for user_hobby in user_hobbies]

    @classmethod
    def get_most_common_user(cls, user_id: int) -> User:
        """Search for the user with the most common hobbies with the given user."""
        user_hobbies = UserHobby.query.filter_by(user_id=user_id).all()
        user_hobby_ids = [user_hobby.hobby_id for user_hobby in user_hobbies]

        # Find users who share the same hobbies
        shared_hobbies = (
            db.session.query(UserHobby.user_id, db.func.count(UserHobby.hobby_id).label("shared_count"))
            .filter(UserHobby.hobby_id.in_(user_hobby_ids))
            .filter(UserHobby.user_id != user_id)
            .group_by(UserHobby.user_id)
            .order_by(db.func.count(UserHobby.hobby_id).desc())
            .first()
        )

        if not shared_hobbies:
            raise UserException("No other users share hobbies with the given user.")

        # TODO: if most_common_user is not found, we should use the hobby similarity
        # table to find the most similar user.

        # Get the user with the most shared hobbies
        most_common_user_id = shared_hobbies.user_id
        return User.query.get(most_common_user_id)
