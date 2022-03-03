import datetime
import traceback
import json

from ..cards.api import cards_get_dict
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

bp = Blueprint('cards_manager', __name__, url_prefix='/dashboard/cards')


@bp.route('/', methods=('GET',)) 
@auth_check_dashboard(redirect_to_login=True)
def index(user):
	try:
		data = cards_get_dict()
	except Exception as e:
		err_id = u.get_error_id()

		current_app.logger.error('[ Get cards list error (cards_manager)| error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

		int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
		return make_response( int_error, 500 )
 
	return render_template('dashboard/cards_manager.html', data=data)
