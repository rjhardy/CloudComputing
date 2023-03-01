import csv
import sqlite3
import os

from flask import Flask, request, g, render_template, url_for, flash, redirect, json
from collections import Counter

app = Flask(__name__)

DATABASE = os.path.join(app.root_path,'users.db')

app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/countme/<input_str>')
def count_me(input_str):
    input_counter = Counter(input_str)
    response = []
    for letter, count in input_counter.most_common():
        response.append('"{}": {}'.format(letter, count))
    return '<br>'.join(response)

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT * FROM users""")
    return '<br>'.join(str(row) for row in rows)

@app.route("/username/", methods=('GET', 'POST'))
def username():
    username = request.args.get("username")
    rows = execute_query("""SELECT * FROM users WHERE username = ?""",
                         [username])
    return '<br>'.join(str(row) for row in rows)

@app.route("/createLogin/", methods=('GET', 'POST'))
def createLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username:
            flash('Username is required!')
        elif not password:
            flash('Password is required!')
        else:
            conn = get_db()
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('updateUser', username=username))
    return render_template('createLogin.html')

@app.route("/updateUser/", methods=('GET', 'POST'))
def updateUser():
    username = request.args.get("username")
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        if not firstname:
            flash('First name is required!')
        elif not lastname:
            flash('Last Name is required!')
        elif not email:
            flash('Email is required!')
        else:
            conn = get_db()
            conn.execute("UPDATE users SET firstname = ?, lastname = ?, email = ? WHERE username = ?",(firstname, lastname, email, username))
            conn.commit()
            conn.close()
            return redirect(url_for('username', username=username))
    return render_template('updateUser.html')

@app.route("/lookupExistingUser/", methods=('GET', 'POST'))
def lookupExistingUser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username:
            flash('Username is required!')
        elif not password:
            flash('Password is required!')
        else:
            user = json.dumps({"usernameEntered":username, "password":password})
            return redirect(url_for('existingUser', user=user))
    return render_template('lookupExistingUser.html')

@app.route("/existingUser/", methods=('GET', 'POST'))
def existingUser():
    userTemp = request.args.get("user")
    user = json.loads(userTemp)
    username = user['usernameEntered']
    password = user['password']
    rows = execute_query("""SELECT * FROM users WHERE username = ? AND password = ?""",
                         (username, password))
    return '<br>'.join(str(row) for row in rows)


if __name__ == '__main__':
  app.run(host="0.0.0.0",port=8080,debug=True)

