from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def add_user(username, password) -> bool:
    if get_user(username):
        return True
    
    hashed_password = password #generate_password_hash(password, method='pbkdf2:sha256') # TODO
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return False

def get_user(username):
    return User.query.filter_by(username=username).first()

def check_user_password(user, password) -> bool:
    return password == password
    # return check_password_hash(user.password, password) # TODO