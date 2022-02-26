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

from ..db import get_db, sqlite3
# from ..auth import auth_check_dashboard, User
# from .. import utils as u

# from . import cards_manager
# from . import users_analytics

from . import api
from .. import user

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

	badge_page = request.path + "/badges?card_id={}".format(card_id) 

	return render_template('cards/single_card.html', 
							card_data=card_data,
							badge_page=badge_page, 
							next_card=next_card,
							prev_card=prev_card)

enigma_keys = ["enigma{}".format(i) for i in range(10)]

@bp.route('/badges', methods=('GET', 'POST')) 
def badges():
	card_id = request.args.get('card_id')

	c_uid = session.get('_caccia_user_id', None)
	if not c_uid:
		return render_template('cards/init.html', first_card=request.path+"?card_id=0")		

	if card_id:
		try:
			card_id = int(card_id)
		except Exception as e:
			flash("card_id should be an integer")
			return render_template('cards/home.html')

	new_badge = -1
	if request.method == 'POST':
		if not card_id:
			flash("A card_id is required to POST a new badge")
			return render_template('cards/home.html')

		play_time = request.form.get('play_time')
		
		enigma_key = None
		try:
			enigma_key = enigma_keys[card_id]
		except (KeyError, IndexError):
			flash("Card not found: {}".format(card_id))
			return render_template('cards/home.html')

		db = get_db()
		db.execute('''UPDATE users SET 
					lastseen = CURRENT_TIMESTAMP,
					firstanswer = case when firstanswer then
									firstanswer
								   else
									CURRENT_TIMESTAMP
								   end,
					playtime = playtime + ?,
					{} = ?
					WHERE id = ?;'''.format(enigma_key), (play_time, 1, c_uid))
		db.commit()	
		new_badge = card_id

	user_data = user.user_get_dict(c_uid)
	if not user_data:
		return render_template('cards/init.html', first_card=request.path+"?card_id=0")

	user_badges = [user_data["enigma0"], user_data["enigma1"], user_data["enigma2"],
					user_data["enigma3"], user_data["enigma4"], user_data["enigma5"],
					user_data["enigma6"], user_data["enigma7"], user_data["enigma8"],
					user_data["enigma9"]]
	
	if card_id:
		card_data = api.cards_get_dict(card_id)
		map_image = card_data[0]["map_image"]
		back_to_card = request.path+"?card_id={}".format(card_id)
	else:
		map_image = None
		back_to_card = None

	return render_template('cards/badge.html',
							back_to_card = back_to_card, 
							new_badge= new_badge, 
							user_badges= user_badges,
							map_image= map_image)

