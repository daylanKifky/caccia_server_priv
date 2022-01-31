import datetime

from flask import (
    Blueprint, current_app, g, redirect, render_template, request, 
    url_for, make_response, jsonify, session, g
)
from werkzeug.exceptions import abort
from functools import wraps

import firebase_admin
from firebase_admin import credentials, auth

from .db import get_db
# from . import utils as u
# from . debug_user import get_debug_uid


class User(auth.UserRecord):
    pass

class UserLite:
    def __init__(self, uid, email):
        self.uid = uid
        self.email = email


def get_firebase():
    if 'firebase' not in g:
        try:
            g.firebase = firebase_admin.get_app()
        except Exception as e:
            cred = credentials.Certificate(current_app.config["FIREBASE_CONF"])
            g.firebase = firebase_admin.initialize_app(cred)

    return g.firebase

# see https://firebase.google.com/docs/auth/admin/verify-id-tokens#python

def create_user_dashboard(email, password):
    #see:
    # https://github.com/firebase/firebaseui-web/issues/99#issuecomment-352377146
    # https://stackoverflow.com/questions/38357554/how-to-disable-signup-in-firebase-3-x
    fbase = get_firebase()
    try:
        user = auth.create_user(email = email, password=password)

    except ValueError as e:
        return "The passed values are not correct: {}".format(e)        
    except Exception as e:
        return "There was an error creating the user: {}".format(e)
        
    try:
        firebase_admin.auth.set_custom_user_claims(user.uid, {'dashboard_access': True}, app=None)

    except ValueError as e:
        return "The passed custom claim or uid are invalid: {}".format(e)        
    except Exception as e:
        return "There was an error creating the user (custom claim): {}".format(e)
    
    user.__class__ = User
    return user        

def auth_check(check_time = True):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = None
            if 'x-access-tokens' in request.headers:
                token = request.headers['x-access-tokens']

            if not token:
                content = jsonify({'message': 'a valid token is missing'})
                return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "login required"'})

            #==== Debug user:
            # if current_app.config['DEBUG'] and "_dev_" in token:
            #     recreate = False
            #     if "new" in token:
            #         recreate = True
            #     uid = get_debug_uid(recreate)
            #     return f(uid, *args, **kwargs)
            
            #==== Production user:
            fbase = get_firebase()

            try:
                decoded_token = auth.verify_id_token(token)
                
            except Exception as e:
                content = jsonify({'message': 'The token is not valid or has expired'})
                return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "id token expired"'})

            uid = decoded_token['uid']

            db = get_db()
            now = datetime.datetime.now()
            if check_time:
                row = db.execute( 'SELECT last_request from user WHERE id = ?;', 
                    (uid, ) ).fetchone()

                if not row:
                    return f(uid, *args, **kwargs)

                min_time = current_app.config['MIN_TIME_REQUESTS']

                if (now - row["last_request"]) < datetime.timedelta(seconds = min_time):
                    content = jsonify({'message': 'You are too fast, wait {} seconds between requests'.format(min_time)})
                    return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "you are too fast"'})


            db.execute('UPDATE user SET last_request = ? WHERE id = ?;', (now, uid))
            db.commit()

            return f(uid, *args, **kwargs)
        
        return wrapper
    return decorator

def auth_check_dashboard(redirect_to_login = False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            g.user = None
            if request.method == 'POST' and not (session and session.get('user_uid', False)):
                token = None
                if 'x-access-tokens' in request.headers:
                    token = request.headers['x-access-tokens']

                if not token:
                    content = jsonify({'message': 'a valid token is missing'})
                    return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "login required"'})

                fbase = get_firebase()

                try:
                    decoded_token = auth.verify_id_token(token)
                    g.user = auth.get_user(decoded_token['uid'])
                    current_app.logger.debug("User {} with provider {} logged".format(g.user.email, g.user.provider_id))

                except firebase_admin.auth.InvalidIdTokenError as e:
                    content = jsonify({'message': 'The token is not valid'})
                    return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "id token not valid"'})

                except firebase_admin.auth.ExpiredIdTokenError as e:
                    content = jsonify({'message': 'The token has expired'})
                    return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "id token expired"'})

                except Exception as e:
                    content = jsonify({'message': 'Error in authentication. Contact the system administrator'})
                    return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "Authentication failed"'})

                provider = decoded_token['firebase']['sign_in_provider']
                allowed = decoded_token.get('dashboard_access', False)

                #418
                # if not allowed or provider != 'password' or g.user.provider_id != 'firebase':
                #     current_app.logger.error("User {} with provider {} tried to log in from {}".format(g.user.email, provider, request.remote_addr))
                #     content = jsonify({'message': 'User not allowed to access this page'})
                #     return make_response(content,  401,  {'WWW.Authentication': 'Basic realm: "user not allowed"'})

                session.clear()
                session['user_email'] = g.user.email
                session['user_uid'] = g.user.uid

            elif request.method == 'GET' or (session and session.get('user_uid', False)):
                email = session.get('user_email', False)
                uid = session.get('user_uid', False)

                if uid and email:
                    g.user = UserLite(uid, email)
                elif redirect_to_login:
                    return redirect(url_for("dashboard.login"))

            else:
                return "Method not allowed", 405

            # returns https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#userinfo
            return f(g.user, *args, **kwargs)
        
        return wrapper
    return decorator