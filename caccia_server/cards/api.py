import datetime
import traceback

from flask import (
    Blueprint, current_app, g, redirect, 
    render_template, request, url_for, 
    make_response, jsonify
)
from werkzeug.exceptions import abort
from functools import wraps
from os.path import join

from ..db import get_db
from .. import utils as u

bp = Blueprint('api_cards', __name__, url_prefix='/cards')


def cards_get_dict(card_id = None):
    response = []
    
    db = get_db()
    
    if card_id is None:
        res = db.execute("SELECT * FROM cards")
        res = res.fetchall()
    
    else:
        res = db.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        res = res.fetchall()

    for row in res:
        response.append({k:row[k] for k in row.keys()})

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
                      mapimage = ?,
                      modified = CURRENT_TIMESTAMP
                    WHERE id = ?;''', (content['image'], content['enigmatype'], 
                    content['question'], content['answer'], content['mapimage'], content['id']))
        
        db.commit()

    except Exception as e:
        err_id = u.get_error_id()

        current_app.logger.error('[ Post cards content error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

        int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
        return make_response( int_error, 500 )


    return jsonify({"status": "ok"})


@bp.route('/image/', methods=('POST',)) 
# @auth_check_dashboard(redirect_to_login=True)
def image(user=None):
    try:
        if 'file' not in request.files:
            return jsonify({"status": "image not saved, file not present in request"})

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return jsonify({"status": "image not saved, empty file in request"})

        if 'Content-length' not in request.headers:
            raise u.Download_Image_Error("No Content-length header in request")

        if int(request.headers['Content-length']) > current_app.config['MAX_IMG_SIZE']:
            raise u.Download_Image_Error("The image {} is too big, max allowed {}kb".format(file.filename, current_app.config['MAX_IMG_SIZE']/1024))
    
        saved_image, image_path = u.save_image(file)
        image_url = join(request.host_url, image_path)

    except u.Download_Image_Error as e:
        err_id = u.get_error_id()

        int_error = jsonify({"status": "error", "reason": "Image upload error: {}".format(e), "error_id": err_id})
        current_app.logger.error('[ Post cards image Upload error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

        return make_response( int_error, 500 )


    except Exception as e:
        err_id = u.get_error_id()

        current_app.logger.error('[ Post cards generic image error | error_id: %s ] %s\n%s---' % (err_id, e, traceback.format_exc()) )

        int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
        return make_response( int_error, 500 )
    

    return jsonify({"status": "ok", "saved_image": saved_image, "image_url": image_url})
