from flask import Flask, redirect, render_template, request, session, url_for, g, flash, abort
import sqlite3

'''
Got a lot of the information from the following sources:
1. https://www.youtube.com/watch?v=2Zz97NVbH0U
2. https://www.tutorialspoint.com/flask/flask_sessions.htm
3. https://www.geeksforgeeks.org/python-introduction-to-web-development-using-flask
4. https://www.tutorialspoint.com/flask/flask_message_flashing.htm
5. https://www.sqlitetutorial.net/sqlite-python/
6. https://likegeeks.com/python-sqlite3-tutorial/
7. https://flask.palletsprojects.com/en/1.0.x/patterns/sqlite3/
8. https://pythonise.com/series/learning-flask/python-before-after-request
9. https://stackoverflow.com/questions/44507085/how-to-reopen-sqlite-connection-in-flask-app?fbclid=IwAR1CvOwY-_PDbxr188klPW-B8YtLD28HvyNmxRZ1mChkEnmT1CARUCo7ywc
10. https://www.youtube.com/watch?v=DFCKWhoiHZ4&fbclid=IwAR0oE6lVjDKdgHoXClTiOrP9E-Gbh5dmhg_dRj6P24L3NSTbLeOBt4Dp-fs
'''

# Creates error messages for when students attempt to view instructors' webpages and vice versa.
unauthorized_instructor_login_message = "Status Code 403: As an instructor, you are not allowed to look at the students' webpages."
unauthorized_student_login_message = "Status Code 403: As a student, you are not allowed to look at the instructors' webpages."

# Got these 4 functions from https://flask.palletsprojects.com/en/1.0.x/patterns/sqlite3/.
# They were also in Professor Attarwala's week 11 lecture video and week 12 tutorial notes.
DATABASE = "assignment3.db"

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

        # Got this from https://stackoverflow.com/questions/44507085/how-to-reopen-sqlite-connection-in-flask-app?fbclid=IwAR1CvOwY-_PDbxr188klPW-B8YtLD28HvyNmxRZ1mChkEnmT1CARUCo7ywc
        g.pop('_database')

# Got this from https://pythonise.com/series/learning-flask/python-before-after-request
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

# These are the functions for the login page and for creating a new account.
# The index will redirect the user to the log in page.
@app.route('/')
def index():
	return redirect(url_for('login'))

# The login page.
@app.route('/login', methods=["GET", "POST"])
def login():

	
	# Removes the user id if there is one inside the session.
	# This way, if the user goes to the login page from any other page, they must login again. 
	session.pop('user_id', None)

	if(request.method == "POST"):

		# Gets the username and password the user enters.
		username = request.form['username']
		password = request.form['password']

		# Querying the database to see if the username and password the user inputted is valid or not.
		db = get_db()
		db.row_factory = make_dicts
		userid = query_db('''SELECT NumberID FROM User WHERE Username=? AND Password=?''', [username, password], one=True)
		close_connection(None)
		# The user has entered a valid username/password.
		if(userid is not None):

			# Gets the user's student/professor id. We will use this to distinguish the two types of users.
			# All students have a student number of 3 digits and all professors have a professor number of 1 digit.
			session['user_id'] = userid['NumberID']
			session['logged_in'] = True

			# Redirects the user to their respective home page.
			if(len(str(session['user_id'])) == 3):
				return redirect(url_for('student_home'))
			else:
				return redirect(url_for('instructor_home'))
		else:
			# Creates an error message with flash.
			# I learned how to use flash here: https://www.youtube.com/watch?v=DFCKWhoiHZ4&fbclid=IwAR0oE6lVjDKdgHoXClTiOrP9E-Gbh5dmhg_dRj6P24L3NSTbLeOBt4Dp-fs
			flash('You have entered an invalid username and/or password. Please Try Again.')
	return render_template('index.html')

@app.route('/ChooseUser', methods=["GET", "POST"])
def choose_user():
	'''
	A function that lets the user choose whether they are a student or instructor.
	'''
	if(request.method == "POST"):

		# Gets the user type (student or instructor) that the user chose.
		user_type = request.form['user_type']

		# If the user is a student, then we redirect them to the page that creates accounts for students.
		if (user_type == "Student"):
			return redirect(url_for('create_new_student_account'))
		# Otherwise, we redirect them to the page that creates accounts for instructors.
		else:
			return redirect(url_for('create_new_instructor_account'))

	return render_template('ChooseUser.html')

# This is the page that let's the student create an account.
@app.route('/CreateNewStudentAccount', methods=["GET", "POST"])
def create_new_student_account():
	'''
	This function takes the user to the page that creates accounts for students.
	'''

	# This is what the user will see after they input data to create a new account.
	return_message = None

	if(request.method == "POST"):

		# Gets the first name, last name, username, password and student number the user inputted.
		firstname = request.form['firstname']
		lastname = request.form['lastname']
		username = request.form['new_username']
		password = request.form['new_password']
		student_number = request.form['student_number']

		# Sets return_message to be the output of create_login_message after we check if the username, password and account number
		# is unique or not.
		return_message = create_login_message(check_info_in_database(firstname, lastname, username, password, student_number))
		flash(return_message)
	return render_template('CreateNewStudentAccount.html')

# This is the page that let's the instructor create an account.
@app.route('/CreateNewInstructorAccount', methods=["GET", "POST"])
def create_new_instructor_account():
	'''
	This function takes the user to the page that creates accounts for instructors.
	'''

	# This is what the user will see after they input data to create a new account.
	return_message = None

	if(request.method == "POST"):

		# Gets the first name, last name, username, password and student number the user inputted.
		firstname = request.form['firstname']
		lastname = request.form['lastname']
		username = request.form['new_username']
		password = request.form['new_password']
		instructor_number = request.form['instructor_number']

		# Sets return_message to be the output of create_login_message after we check if the username, password and account number
		# is unique or not.
		return_message = create_login_message(check_info_in_database(firstname, lastname, username, password, instructor_number))
		flash(return_message)
	return render_template('CreateNewInstructorAccount.html')

def check_info_in_database(firstname, lastname, username, password, id_number):
	'''
	This function takes all the information (username, password, student/instructor number) and
	checks whether or not they already exist in the database.
	If the username, password and student/instructor number does not exist in the database, we will store the new information
	in there.
	This will return a tuple that looks like this: (unique_username, unique_password, unique_id_number) to allow the other functions
	to know if all the info is unique or not.
	'''

	# Used to keep track if the username and id number are unique or not.
	# We allow the password to be the same.
	unique_username = True
	unique_user_number = True

	# Creates a connection to the db to query for the username, password and student/instrucot number.
	db = get_db()
	db.row_factory = make_dicts

	# Queries the database to see if there's any user id or username that matches the inputted ones.
	query_user_number = query_db('''SELECT * FROM User WHERE NumberID=?''', [id_number])
	query_username = query_db('''SELECT * FROM User WHERE Username=?''', [username])
	close_connection(None)
	
	# If query_username has something in it, then we know that the username is taken, and so
	# we set unique_username to False.
	if (len(query_username) > 0):
		unique_username = False

	# If query_user_number has something in it, then we know that the student/instructor number is taken, and so
	# we set unique_user_number to False.
	if (len(query_user_number) > 0):
		unique_user_number = False

	# If all three items are unique, then we insert it into the database.
	if(unique_username and unique_user_number):
		# Creates a connection to the db to insert the information.
		# Got this part from https://mstrzhang.github.io/cscb20/2019/03/31/week13.html
		db = get_db()
		db.row_factory = make_dicts

		# make a new cursor from the database connection
		cur = db.cursor()

		# Inserting the user's information into the database for the user table.
		cur.execute('INSERT INTO User (FirstName, LastName, NumberID, Username, Password) VALUES (?, ?, ?, ?, ?)', [
					firstname,
					lastname, 
					id_number,
					username, 
					password 
				    ])
		db.commit()

		# If we're creating a new student account, we're also going to input information into the marks table.
		# I will pre-set all grades to be 0.
		if (len(id_number) == 3):
			# Inserting the user's information into the database for the mark's table.
			cur.execute('INSERT INTO Marks (StudentNumber, Assignment1, Assignment2, Assignment3, Labs, Midterm, Exam) VALUES (?, ?, ?, ?, ?, ?, ?)', [
						int(id_number),
						0,
						0,
						0,
						0,
						0,
						0
					    ])
			db.commit()
		cur.close()

	return (unique_username, unique_user_number)

def create_login_message(status):
	'''
	This function creates the login message when the user tries to create a new account.
	It takes in a tuple of True or False for username, password and user number.
	True means that the item is unique.
	False means that the item is taken.
	'''
	message = ""

	# If the username, password, or user number is False, we will let the user know that
	# it has been taken.
	if (not status[0]):
		message += "That username is taken.\n"

	if (not status[1]):
 		message += "That user number is taken.\n"

	# If all three items are unique, we let the user know that their account has been created.
	if(status[0] and status[1]):
		message += "Congratulations. Your account has been created."
	
	return message

# These are the webpages that only students will see when they log in.
# What a student will see when they log in successfully.
@app.route('/StudentHome')
def student_home():
	# If the user tries to access any page before logging in, they will be redirected to the login page.
	if (not g.user):
		return redirect(url_for('login'))
	else:
		# This checks if the the user is a student or an instructor.
		# If it's a student, then we take them to the Student Home page.
		# Otherwise, we throw an HTTP Status 403 Code.
		if(len(str(session['user_id'])) == 3):
			return render_template('StudentHome.html')
		else:
			# Throws an HTTP Status 403 Code.
			abort(403, unauthorized_instructor_login_message)

# Creates the route for Feedback.html.
@app.route('/Feedback', methods=["GET", "POST"])
def feedback():
	# If the user tries to access any page before logging in, they will be redirected to the login page.
	if not g.user:
		return redirect(url_for('login'))
	else:
		# This checks if the the user is a student or an instructor.
		# If it's a student, then we take them to the Feedback page.
		# Otherwise, we throw an HTTP Status 403 Code.
		if(len(str(session['user_id'])) == 3):
			# Gets the information the user submitted.
			if(request.method == "POST"):

				'''
				Got this part from https://mstrzhang.github.io/cscb20/2019/03/31/week13.html
				'''
				db = get_db()
				db.row_factory = make_dicts

				# make a new cursor from the database connection
				cur = db.cursor()

				# Inserting students' feedback of the professors into the database.
				cur.execute('''INSERT INTO Feedback (InstructorName, Question1, Question2, Question3, Question4) VALUES (?, ?, ?, ?, ?)''', [
							request.form['instructor_name'],
						    request.form['question1'],
						    request.form['question2'],
						    request.form['question3'],
						    request.form['question4'],
						    ])
				db.commit()
				cur.close()

			# Opens the database to make a connection.
			db = get_db()
			db.row_factory = make_dicts

			# Gets the names of all instructors.
			instructor_names = query_db('''SELECT FirstName, LastName FROM User WHERE NumberID<=9''')
			close_connection(None)
			instructor_names_formatted = []
			# Changes the content of the instructor_names array.
			'''
			Instead of having {firstname: x, lastname: y}, I want to have {Name: firstname lastname}
			to make it easier to iterate in Feedback.html.
			'''
			for item in instructor_names:
				name = {}
				name.update({"Name" : item['FirstName'] + item['LastName']})
				instructor_names_formatted.append(name)

			return render_template('Feedback.html', instructorNames=instructor_names_formatted)
		else:
			# Throws an HTTP Status 403 Code.
			abort(403, unauthorized_instructor_login_message)


@app.route('/logout')
def logout():
	# Removes the user's session and redirects them to the login page.
	session.pop('user_id', None)
	return redirect(url_for('login'))

if (__name__ == "__main__"):
	# Creates a secret key.
	app.secret_key = b"secretkey"
	app.run(debug = True)