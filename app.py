from flask import Flask, redirect, render_template, request, session, url_for, g, flash, abort
import sqlite3


DATABASE = "schedule.db"

# connects to the database
def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

# converts the tuples from get_db() into dictionaries
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# given a query, executes and returns the result
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

app = Flask(__name__)

# this function must come after the instantiation of the variable app
# (i.e. this comes after the line app = Flask(__name__))
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()

        g.pop('_database')

@app.before_request
def before_input():

	# Initalizes g.user to be None so that if a user tries to access any page before logging in, they will be redirected
	# to the login page.
	g.user = None
	if ('user_id' in session):

		# This gets the user's first and last name and stores it in g.user.
		db = get_db()
		db.row_factory = make_dicts
		name = query_db('''SELECT FirstName, LastName FROM User WHERE NumberID=?''', [session['user_id']], one=True)
		close_connection(None)
		g.user = name['FirstName'] + " " + name['LastName']


@app.route('/')
def index():
	return render_template('index.html')


if (__name__ == "__main__"):
	# Creates a secret key.
	app.secret_key = b"secretkey"
	app.run(debug = True)