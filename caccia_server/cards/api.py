import datetime
import traceback

from flask import (
    Blueprint, current_app, g, redirect, 
    render_template, request, url_for, 
    make_response, jsonify
)
from werkzeug.exceptions import abort
from functools import wraps

from ..db import get_db
from .. import utils as u

bp = Blueprint('api_cards', __name__, url_prefix='/cards')

def cards_get_dict(card_id = None):
    response = []
    
    try:
        db = get_db()
        
        if card_id is None:
            res = db.execute("SELECT * FROM cards")
            res = res.fetchall()
        
        else:
            res = db.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
            res = res.fetchall()

        for row in res:
            response.append({k:row[k] for k in row.keys()})
        
    except Exception as e:
        pass

    return response

@bp.route('/', methods=('GET',)) 
def cards_get():
    try:
        db = get_db()
        
        res = db.execute("SELECT * FROM cards")
        res = res.fetchall()

        response = []
        for row in res:
            response.append({k:row[k] for k in row.keys()})
        
    except Exception as e:
        err_id = u.get_error_id()

        current_app.logger.error('[ Get cards list error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

        int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
        return make_response( int_error, 500 )

    return jsonify(response)
    
@bp.route('/', methods=('POST',))
# @auth_check_dashboard(redirect_to_login=True) 
def populate_msg():
    content = request.get_json()

    try:
        db = get_db()
        db.execute(
                ''' UPDATE cards
                    SET image = ? ,
                      enigmatype = ? ,
                      question = ?,
                      answer = ?,
                      modified = CURRENT_TIMESTAMP
                    WHERE id = ?;''', (content['image'], content['enigmatype'], 
                    content['question'], content['answer'], content['id']))
        
        db.commit()

    except Exception as e:
        err_id = u.get_error_id()

        current_app.logger.error('[ Post cards content error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

        int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
        return make_response( int_error, 500 )


    return jsonify({"status": "ok"})