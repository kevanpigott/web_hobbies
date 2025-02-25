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

    def init_db(app) -> None:
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def get_user(username: str) -> User:
        """given a username, return the user object"""
        return User.query.filter_by(username=username).first()

    def get_user_by_id(user_id: int) -> User:
        """given a user_id, return the user object"""
        return User.query.get(user_id)

    def add_user(username: str, password: str) -> None:
        """given user details, add a new user"""
        if __class__.get_user(username):
            raise UserException("Username already exists! Try again.")

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        new_user = User(
            username=username,
            password=hashed_password.decode("utf-8"),
            email=f"{username}@fake_email.com",
        )
        db.session.add(new_user)
        db.session.commit()

    def check_user_password(user: User, password: str) -> bool:
        """given a user object and a password, check if password is correct"""
        return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))

    def calculate_all_relations_for_hobby(hobby: Hobby) -> None:
        # TODO: Implement this function
        pass

    def add_hobby_to_user(user_id: int, hobby_name: str) -> Hobby:
        """given a user and a hobbie, create a new Hobby if it does not exits,
        link the user to the hobby in the UserHobby table
        """
        hobby_name = hobby_name.strip().lower()
        if not hobby_name:
            raise UserException("Hobby name cannot be empty!")

        # check if User exists
        user = User.query.get(user_id)
        if not user:
            raise UserException("User does not exist!")

        # check if Hobby exists
        existing_hobby = Hobby.query.filter_by(name=hobby_name).first()
        if not existing_hobby:
            existing_hobby = Hobby(name=hobby_name)
            db.session.add(existing_hobby)
            db.session.commit()
            __class__.calculate_all_relations_for_hobby(existing_hobby)

        # Ensure the hobby has a valid ID
        if existing_hobby.id is None:
            raise UserException("Failed to add hobby to the database!")

        # check if UserHobby already exists
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

    def remove_hobby_from_user(user_id: int, hobby_id: str) -> None:
        """given a user and a hobby, remove the hobby from the user"""
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

    def get_user_hobbies(user_id: int) -> list[Hobby]:
        """given a user, return a list of hobbies"""
        user_hobbies = UserHobby.query.filter_by(user_id=user_id).all()
        # get the hobby names
        return [Hobby.query.get(user_hobby.hobby_id) for user_hobby in user_hobbies]

    def number_of_hobbies():
        return Hobby.query.count()

    def get_most_popular_hobbies(limit=15, offset=0):
        return Hobby.query.order_by(Hobby.user_count.desc()).limit(limit).offset(offset).all()

    def recount_hobbies():
        hobbies = Hobby.query.all()
        for hobby in hobbies:
            hobby.user_count = UserHobby.query.filter_by(hobby_id=hobby.id).count()
        db.session.commit()

    def get_hobby(hobby_id: int) -> Hobby:
        return Hobby.query.get(hobby_id)

    def get_users_by_hobby(hobby_id: int) -> list[User]:
        user_hobbies = UserHobby.query.filter_by(hobby_id=hobby_id).all()
        return [User.query.get(user_hobby.user_id) for user_hobby in user_hobbies]
