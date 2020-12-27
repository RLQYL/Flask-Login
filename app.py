from flask import Flask, redirect, render_template, request, session, url_for, flash, abort
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

# Creates the tables.
db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user != None:
            session["id"] = username
            return redirect(url_for('home')) # url_for takes in a function parameter
        else:
            flash("Login Failed!")
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
            session["id"] = username
            return redirect(url_for('home'))
        else:
            flash("That username is taken.")
    return render_template('CreateAccount.html')   

@app.route('/homepage')
def home():
    if (len(session) == 0):
        return(abort(403))
    name = User.query.filter_by(username=session["id"]).first()
    user_name = name.firstname + " " + name.lastname
    return render_template('Home.html', name=user_name)

@app.route('/logout')
def logout():
    # Removes the user's session and redirects them to the login page.
    session.pop('id', None)
    return redirect(url_for('index'))


if (__name__ == "__main__"):
	# Creates a secret key.
	app.secret_key = b"secretkey"
	app.run(debug = True)