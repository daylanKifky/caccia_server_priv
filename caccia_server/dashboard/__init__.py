import datetime
import traceback

from urllib.parse import urlparse, urljoin

from flask import (
	Blueprint, current_app, g, redirect, 
	render_template, request, url_for, 
	make_response, jsonify, session, flash
)
from werkzeug.exceptions import abort
from functools import wraps

from ..db import get_db, sqlite3
from ..auth import auth_check_dashboard, User
# from .. import utils as u

from . import cards_manager
from . import users_analytics

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def register_blueprints(app):
	app.register_blueprint(bp)
	app.register_blueprint(cards_manager.bp)
	app.register_blueprint(users_analytics.bp)

#https://github.com/firebase/quickstart-js/blob/bdd17258e33c017eaf0fd5d09eaeacbbdaa6f1fa/auth/email-password.html#L60-L73
#
#
@bp.route('/login', methods=('GET', 'POST'))
@auth_check_dashboard()
def login(user):
	if request.method == 'POST':
		return redirect(url_for("dashboard.index"))

	return render_template('auth/login.html')

@bp.route('/', methods=('GET',)) 
@auth_check_dashboard(redirect_to_login=True)
def index(user):
	if user:
 		return redirect(url_for("cards_manager.index"))
	else:
		
		return redirect(url_for("dashboard.login"))


@bp.route('/logout', methods=('GET',)) 
def logout():
	session.clear()
	return redirect(url_for('dashboard.index'))


@bp.route('/error', methods=('GET',)) 
def error():
	session.clear()
	current_app.logger.error("Richiesta de accesso dashboard non riuscita da {}, message:{}"
		.format(request.remote_addr, request.args.get('reason', "(not present)")))

	flash("Login error: {}".format(request.args.get('msg', "errore sconosciuto")))
	return redirect(url_for('dashboard.login'))
