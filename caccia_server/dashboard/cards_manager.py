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

bp = Blueprint('cards_manager', __name__, url_prefix='/dashboard/cards')


@bp.route('/', methods=('GET',)) 
@auth_check_dashboard(redirect_to_login=True)
def index(user):
	data = { "some_var" : "pippo", "foo": "pappa" }
	return render_template('cards_manager.html', data=json.dumps(data), **data)
