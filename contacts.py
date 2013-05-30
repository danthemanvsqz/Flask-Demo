#all the imports
from __future__ import with_statement
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
 flash

#configuration
DATABASE = '/tmp/contacts.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create app
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

@app.route('/')
def show_contacts():
	cur = g.db.execute('select lname, fname, email, phone from contacts order by id desc')
	contacts = [dict(lname=row[0], fname=row[1], email=row[2], phone=row[3]) 
					for row in cur.fetchall()]
	return render_template('show_contacts.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into contacts(lname, fname, email, phone) values (?,?,?,?)',
				[request.form['lname'], request.form['fname'], request.form['email'],
				request.form['phone']])
	g.db.commit()
	flash('New contact successfully input')
	return redirect(url_for('show_contacts'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_contacts'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_contacts'))


if __name__ == '__main__':
	app.run()
