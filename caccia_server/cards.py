import datetime
import traceback

from flask import (
    Blueprint, current_app, g, redirect, 
    render_template, request, url_for, 
    make_response, jsonify
)
from werkzeug.exceptions import abort
from functools import wraps

from .db import get_db

bp = Blueprint('cards', __name__, url_prefix='/cards')

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
        raise e
        # err_id = u.get_error_id()

        # current_app.logger.error('[ Register game start error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )
        err_id = 418

        int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
        return make_response( int_error, 500 )

    return jsonify(response)
    
@bp.route('/', methods=('POST',))
# @auth_check_dashboard(redirect_to_login=True) 
def populate_msg():
    
    content = request.get_json()
    db = get_db()
    db.execute(
            ''' UPDATE cards
                SET image = ? ,
                  enigma_type = ? ,
                  question = ?,
                  answer = ?
                WHERE id = ?;''', (content['image'], content['enigma_type'], 
                content['question'], content['answer'], content['id']))
    
    db.commit()
    return jsonify({"status": "ok"})