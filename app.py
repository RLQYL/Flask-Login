from flask import Flask, redirect, render_template, request, session, url_for, g, flash, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedule.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    firstname = db.Column(db.String(10))
    lastname = db.Column(db.String(10))
    username = db.Column(db.String(10))
    password = db.Column(db.String(10))

# class Priority(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     firstname = db.Column(db.String(10))
#     lastname = db.Column(db.String(10))

# Creates the tables.
db.create_all()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        print(user.id)
    return render_template('index.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        if (User.query.filter_by(password=password).first() == None):
            user = User(username=username,
                        password=password,
                        firstname=first_name,
                        lastname=last_name)
            db.session.add(user)
            db.session.commit()
    return render_template('CreateAccount.html')   


if (__name__ == "__main__"):
	# Creates a secret key.
	app.secret_key = b"secretkey"
	app.run(debug = True)