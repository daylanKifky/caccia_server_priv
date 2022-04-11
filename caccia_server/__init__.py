import os
import traceback

from flask import Flask, jsonify, make_response, redirect, url_for
from flask.cli import with_appcontext

from werkzeug.exceptions import NotFound

import firebase_admin
from . import utils as u

import click

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_url_path='/static')
    app.config.from_mapping(
        SECRET_KEY='deva',
        DATABASE=os.path.join(app.instance_path, 'caccia_db.sqlite'),
        FIREBASE_CONF=os.path.join(app.instance_path, 'caccia-3e3b3-firebase-adminsdk-laqso-580a1fec1b.json'),
        # MIN_TIME_REQUESTS = 0.8,
        # FAKE_USERS = 100,
        # MAX_CSV_LINES = 100,
        ALLOWED_IMGS_EXT = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG', '.png'],
        ALLOWED_IMGS_TYPES = ['png', 'jpeg'],
        MAX_IMG_SIZE = 2 * 1024 * 1024, # 2Mb
        # DASHBOARD_USER_CSV = 'dashboard_users.csv'
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # @app.route('/')
    # def not_found():
    #     return make_response(jsonify({'message': 'not found'}), 404)

    # a simple page that report status
    @app.route('/status')
    def hello():
        resp = {'message': 'running'}
        if app.config['DEBUG']:
            resp["env"] = "dev"
        return jsonify(resp) 

    from . import db
    db.init_app(app)

    # from . import user
    # app.register_blueprint(user.bp)
    # app.add_url_rule('/user', endpoint='userbase')

    from . import cards
    app.register_blueprint(cards.bp)
    app.register_blueprint(cards.api.bp)

    from . import user
    app.register_blueprint(user.bp)

    # app.add_url_rule('/base', endpoint='gamebase')

    # from . import quiz
    # app.register_blueprint(quiz.bp)

    # from . import messaggio
    # app.register_blueprint(messaggio.bp)

    from . import dashboard
    dashboard.register_blueprints(app)

    @app.errorhandler(Exception)
    def _(error):
        if isinstance(error, NotFound):
            return make_response( "not found", 404 )
            # return redirect(url_for('not_found'))

        err_id = u.get_error_id()

        app.logger.error('[ Generic error | error_id: %s ] %s\n%s---' % (err_id, error, traceback.format_exc()) )

        int_error = jsonify({"status": "error", "reason": "internal error", "error_id": err_id})
        return make_response( int_error, 500 )


    # @app.cli.command("create-fake-users")
    # @click.argument("num", type=int)
    # def create_fake_users(num):
    #     from . debug_user import make_fake_user
    #     create_users = app.config['FAKE_USERS']

    #     if num:
    #         create_users = num

    #     click.echo("Creating {} fake users".format(create_users))
    #     for i in range(create_users):
    #         uid = "__fake_{:02d}__".format(i)
    #         make_fake_user(uid)
    #         click.echo("user {} created".format(uid))
    
    #     click.echo("Done")


    # @app.cli.command("remove-fake-users")
    # @click.argument("num", type=int)
    # def remove_fake_users(num):
    #     from . debug_user import remove_fake_user
    #     remove_users = app.config['FAKE_USERS']

    #     if num:
    #         create_users = num

    #     click.echo("Removing {} fake users".format(remove_users))
    #     for i in range(remove_users):
    #         uid = "__fake_{:02d}__".format(i)
    #         remove_fake_user(uid)
    #         click.echo("user {} removed".format(uid))
    
    #     click.echo("Done")

    # @app.cli.command("add-dashboard-user")
    # @click.argument("email")
    # def add_dashboard_user(email):
    #     from . auth import create_user_dashboard, User
    #     import csv
    #     password = u.random_pass()

    #     res = create_user_dashboard(email, password)
    #     file = app.config['DASHBOARD_USER_CSV']

    #     if not isinstance(res, User):
    #         click.echo(res)
        
    #     click.echo("Created User with uid:{} | email:{}.".format(res.uid, res.email))

    #     with open(file, 'a+', newline='') as csvfile:
    #         spamwriter = csv.writer(csvfile)
    #         spamwriter.writerow([res.uid, res.email, password])
    #         click.echo("Appended to file {}".format(file))
    #     return



    return app
