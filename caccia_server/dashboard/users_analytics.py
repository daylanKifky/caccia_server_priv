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
	data = { "users_n" : 345, "medium_iq": 6.5 }
	return render_template('dashboard/users_analytics.html', data=json.dumps(data), **data)
