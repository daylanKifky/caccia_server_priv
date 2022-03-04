import datetime
import traceback
import json

from urllib.parse import urlparse, urljoin

from flask import (
	Blueprint, current_app, g, redirect, 
	render_template, request, url_for, 
	make_response, jsonify, session, flash, 
	current_app
)
from werkzeug.exceptions import abort
from functools import wraps

from ..db import get_db, sqlite3
from ..auth import auth_check_dashboard, User
# from .. import utils as u

bp = Blueprint('users_analytics', __name__, url_prefix='/dashboard/users')


@bp.route('/', methods=('GET',)) 
@auth_check_dashboard(redirect_to_login=True)
def index(user):
	try:
		db = get_db()
		
		res = db.execute("SELECT * FROM users")
		res = res.fetchall()

		response = []
		for row in res:

			response.append({k.replace('enigma', 'e'):row[k] for k in row.keys()})
		
	except Exception as e:
		err_id = u.get_error_id()

		current_app.logger.error('[ Get users list error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

		int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
		return make_response( int_error, 500 )

	


	# get all users

	## -- Then filter by:
		# -page (pagination)
		# -username
		# -data?

	#pass them to template
	
	return render_template('dashboard/users_analytics.html', users=response)
