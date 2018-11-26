from flask import Flask, render_template, request, redirect, session, url_for, escape, make_response
from flask_session import Session
from flask_mail import Mail, Message
from flaskext.mysql import MySQL

from functools import wraps
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import secure_filename
import os
from datetime import datetime
from time import clock,time
from multiprocessing import Process


mysql = MySQL()
app = Flask(__name__)

# config file upload
app.config['MAX_CONTENT_PATH'] = 15360 # max file size


# config the database
app.config["CACHE_TYPE"] = "null"
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123pm'
app.config['MYSQL_DATABASE_DB'] = 'pm'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Mail sittings
app.config.update(
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = '',
	MAIL_PASSWORD = '',
	MAIL_DEFAULT_SENDER = ''
	)
mail = Mail(app)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def conn(state):
	def open_conn():
		''' function to open connection with data base'''
		global cursor
		global connect
		try:
			connect = mysql.connect() 
			cursor = connect.cursor()
			return cursor
		except Exception as e:
			return False

	def close_conn():
		'''close connection to database and show error if happend'''
		try:
			cursor.close()
			connect.close
			return True
		except Exception as e:
			#return False
			raise e
	def commit():
		try:
			connect.commit()
			return True
		except Exception as e:
			raise e
			return False

	if state == 'open':
		return open_conn()

	elif state == 'close':
		return close_conn()
	elif state == "commit":
		return commit()
	else:
		return False



