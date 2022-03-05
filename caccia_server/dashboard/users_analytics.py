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
from .. import utils as u
from .. user import create_user_in_db

bp = Blueprint('users_analytics', __name__, url_prefix='/dashboard/users')


@bp.route('/', methods=('GET',)) 
@auth_check_dashboard(redirect_to_login=True)
def index(user):
	pag = int(request.args.get("pag", 0))
	ixpag = int(request.args.get("ixpag", 20))
	uname = request.args.get("uname", "%")
	# dateto = request.args.get("dateto", None)
	# datefrom = request.args.get("datefrom", None)

	page_offset = pag * ixpag
	like_uname = "%{}%".format(uname)
	# uncomment this to create fake users
	# for i in range(100):
	# 	create_user_in_db(u.random_string(6))

	try:
		db = get_db()
		res = db.execute("SELECT COUNT(*) FROM users WHERE username LIKE ?", (like_uname,))
		total_users = res.fetchone()[0]

		# set offset to 0 if requested page exceeds existing ones
		page_offset = page_offset if page_offset + ixpag < total_users else 0 

		res = db.execute("""SELECT * FROM users 
							WHERE username LIKE ? 
							LIMIT ? OFFSET ?""", 
							(like_uname, ixpag, page_offset ))
		res = res.fetchall()

		response = []
		for row in res:

			response.append({k.replace('enigma', 'e'):row[k] for k in row.keys()})
		
	except Exception as e:
		err_id = u.get_error_id()

		current_app.logger.error('[ Get users list error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

		int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
		return make_response( int_error, 500 )

	print("pag +1", pag+1 , "tot/ixpag", total_users // ixpag)

	h = request.path
	u = "" if uname == "%" else "&uname={}".format(uname)
	page_links = {
	"prev_page" : "{}?pag={}{}".format(h, pag-1, u) if pag-1 > 0 else None,
	"next_page" : "{}?pag={}{}".format(h, pag+1, u) if pag+1 < total_users // ixpag else None,
	"first_page" : "{}?pag={}{}".format(h, 0, u),
	"last_page" : "{}?pag={}{}".format(h, total_users // ixpag, u ),
	"total_pages" : total_users // ixpag + 1,
	"this_page" : pag + 1

	}
	print(page_links)

	return render_template('dashboard/users_analytics.html', users=response, **page_links)
