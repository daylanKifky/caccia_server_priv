# import datetime
import traceback

# from urllib.parse import urlparse, urljoin

from flask import (
	Blueprint, current_app, g, redirect, 
	render_template, request, url_for, 
	make_response, jsonify, session, flash
)
from werkzeug.exceptions import abort
# from functools import wraps

from .db import get_db, sqlite3
# from ..auth import auth_check_dashboard, User
from . import utils as u

# from . import cards_manager
# from . import users_analytics

bp = Blueprint('user', __name__, url_prefix='/user')

MAX_CARDS = 10

def create_user_in_db(username):
	db = get_db()
	res = db.execute("""INSERT INTO users(username) VALUES (?)""", (username,))
	db.commit()
	userrow = db.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1;").fetchone()
	uid = userrow["id"]
	current_app.logger.info('User created, id: {}, username: {}'.format(uid, username))

	return uid


@bp.route('/', methods=('POST',)) 
def create_user():
	username = request.form['username']

	try:
		uid = create_user_in_db(username)
	except Exception as error:
		err_id = u.get_error_id()

		current_app.logger.error('[ Error creating user | error_id: %s ] %s\n%s---' % (err_id, error, traceback.format_exc()) )

		flash("Error creating user, please try again or contact the system administrator. Error_id: {}".format(err_id))

		return render_template('cards/init.html')

	session['_caccia_user_id'] = uid
	session['_caccia_user_name'] = username

	return render_template('cards/home.html', first_card=request.url_root+"?card_id=0")

@bp.route('/logout', methods=('GET',)) 
def logout_user():
	session.pop('_caccia_user_id')
	session.pop('_caccia_user_name')
	flash("logout sucessful")
	return render_template('cards/init.html')

def user_get_dict(uid):
	user_dict = {}
	try:
		db = get_db()
		
		res = db.execute("SELECT * FROM users WHERE id = ?", (uid,))
		if not res: return {}
		
		row = res.fetchone()
		user_dict = {k:row[k] for k in row.keys()}

	except Exception as e:
		pass

	return user_dict



