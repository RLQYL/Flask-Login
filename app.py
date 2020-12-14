from flask import Flask, redirect, render_template, request, session, url_for, g, flash, abort
from flask_sqlalchemy import SQLAlchemy

import datetime

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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(10), db.ForeignKey('user.username', ondelete='CASCADE'))
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    priority = db.Column(db.String(10), db.ForeignKey('priority.level', ondelete='CASCADE'))
    completed = db.Column(db.Boolean, default=False)

class Priority(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    level= db.Column(db.String(10))

# Creates the tables.
db.create_all()

@app.route('/')
def index():

    # Checks if the levels are in the db already.
    if Priority.query.filter_by(level="L").first() == None:
        low = Priority(level="L")
        db.session.add(low)
        db.session.commit()

    if Priority.query.filter_by(level="M").first() == None:
        medium = Priority(level="M")
        db.session.add(medium)
        db.session.commit()

    if Priority.query.filter_by(level="H").first() == None:
        high = Priority(level="H")
        db.session.add(high)
        db.session.commit()

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user != None:
            session["id"] = username
            return redirect(url_for('home')) # url_for takes in a function parameter
        else:
            flash("The user does not exist")
    print(len(session))
    return render_template('index.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        if (User.query.filter_by(username=username).first() == None):
            user = User(username=username,
                        password=password,
                        firstname=first_name,
                        lastname=last_name)
            db.session.add(user)
            db.session.commit()
        else:
            flash("The username is taken.")
    return render_template('CreateAccount.html')   

@app.route('/homepage')
def home():
    return render_template('Home.html')

@app.route('/logout')
def logout():
    # Removes the user's session and redirects them to the login page.
    session.pop('id', None)
    return redirect(url_for('login'))


if (__name__ == "__main__"):
	# Creates a secret key.
	app.secret_key = b"secretkey"
	app.run(debug = True)