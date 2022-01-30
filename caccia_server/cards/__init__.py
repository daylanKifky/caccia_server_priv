# import datetime
# import traceback

# from urllib.parse import urlparse, urljoin

from flask import (
	Blueprint, current_app, g, redirect, 
	render_template, request, url_for, 
	make_response, jsonify, session, flash
)
from werkzeug.exceptions import abort
# from functools import wraps

# from ..db import get_db, sqlite3
# from ..auth import auth_check_dashboard, User
# from .. import utils as u

# from . import cards_manager
# from . import users_analytics

from . import api

bp = Blueprint('cards', __name__, url_prefix='/')

MAX_CARDS = 10

@bp.route('/end', methods=('GET',)) 
def end():
	return render_template('cards/end.html')

@bp.route('/', methods=('GET',)) 
def index():
	card_id = request.args.get('card_id')

	c_uid = session.get('_caccia_user_id', None)
	if not c_uid:
		return render_template('cards/init.html', first_card=request.path+"?card_id=0")		

	if not card_id:
		return render_template('cards/home.html', first_card=request.path+"?card_id=0")		

	try:
		card_id = int(card_id)
	except Exception as e:
		flash("card_id should be an integer")
		return render_template('cards/home.html')		

	next_card = card_id + 1
	prev_card = card_id - 1 

	if next_card >= MAX_CARDS:
		next_card = request.path + "end"
	else:
		next_card = request.path + "?card_id={}".format(next_card)

	if prev_card < 0:
		prev_card = request.path
	else:
		prev_card = request.path + "?card_id={}".format(prev_card)
	
	card_data = api.cards_get_dict(card_id)

	if card_data:
		card_data = card_data[0]
	else:
		flash("the requested card_id is not valid: {}".format(card_id))
		return render_template('cards/home.html', first_card=request.path+"?card_id=0")

	return render_template('cards/single_card.html', 
							card_data=card_data, 
							next_card=next_card,
							prev_card=prev_card)

