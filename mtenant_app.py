import random
from flask import Flask, request, g

from mtenant.mtenant_sqlalchemy import MTenantSQLAlchemy, MTUtil

app = Flask(__name__)
db = MTenantSQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base-db.sqlite"
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String)


with app.app_context():
    db.create_all()


@app.route('/')
def bismillah():
    response = "Available Tenant <br>"
    db.get_tenant_list()
    for tenant in db.get_tenant_list():
        response += tenant + "<br>"
    return response


@app.route('/insert')
def insert():
    prefix = ""
    tkey = MTUtil.get_tenant_key()
    if tkey:
        prefix = tkey
    index = random.randint(0, 999)
    user = User(
        username=prefix + "username-" + str(index),
        email=prefix + "email-" + str(index) + "@email.loc")
    db.session.add(user)
    db.session.commit()
    return f"Inserted to tenant {prefix}"


@app.route('/select')
def select():
    response = ""
    users = User.query.all()
    for user in users:
        response += user.username + " " + user.email + "<br>"
    return response


@app.route('/init-tenant')
def init_tenant():
    response = "Tenant Initialized"
    db.register_tenant(app, "db1", "sqlite:///db1.sqlite")
    db.register_tenant(app, "db2", "sqlite:///db2.sqlite")
    db.register_tenant(app, "db3", "sqlite:///db3.sqlite")
    return response


@app.before_request
def before_request():
    tkey = request.args.get("tkey")
    if tkey:
        g.tenant = {"tkey": tkey}


if __name__ == '__main__':
    app.run(debug=True)
