from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import UserException

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Hobby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    user = db.relationship("User", backref=db.backref("hobbies", lazy=True))


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def add_user(username, password):
    if get_user(username):
        raise UserException("Username already exists! Try again.")

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")  # TODO
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()


def get_user(username):
    return User.query.filter_by(username=username).first()


def check_user_password(user, password) -> bool:
    return check_password_hash(user.password, password)  # TODO


def add_hobby(user_id, hobby_name):
    existing_hobby = Hobby.query.filter_by(user_id=user_id, name=hobby_name).first()
    if existing_hobby:
        raise UserException("Hobby already exists for this user!")

    new_hobby = Hobby(user_id=user_id, name=hobby_name)
    db.session.add(new_hobby)
    db.session.commit()
    return new_hobby


def remove_hobby(hobby_id):
    hobby = Hobby.query.get(hobby_id)
    db.session.delete(hobby)
    db.session.commit()


def get_hobbies(user_id):
    return Hobby.query.filter_by(user_id=user_id).all()


def get_all_hobbies():
    return Hobby.query.all()


def get_most_popular_hobbies(limit=15, offset=0):
    return (
        db.session.query(Hobby.name, db.func.count(Hobby.user_id).label("user_count"))
        .group_by(Hobby.name)
        .order_by(db.func.count(Hobby.user_id).desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
