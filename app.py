from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)


with app.app_context():
    db.create_all()


@app.route('/')
def bismillah():
    return "Bismillah Project"

@app.route('/init')
def init():
    user_list = []
    total_record = 20
    for index in range(total_record):
        user_list.append(
            User(
                username="username-" + str(index),
                email="email-" + str(index) + "@email.loc")
        )
    db.session.add_all(user_list)
    db.session.commit()
    return "Initialized"


@app.route('/select')
def select():
    response = ""
    users = User.query.all()
    for user in users:
        response += user.username + " " + user.email + "<br>"
    return response


if __name__ == '__main__':
    app.run(debug=True)
