#!/usr/bin/env python3

'''
Main File for Snaggy my stupid wallbag/pocket replacement that is hopefully
easier to use.
'''

import argparse
import ast
import time
import sys
import json
import logging
import copy
import functools
import base64

import newspaper
import flask
import pymysql

import readconfig
import snaggy_article
import verify_password

if __name__ == "__main__" :

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", help="Config File for Scheduler", required=True)
    parser.add_argument("-v", "--verbose", action='store_true', help="Turn on Verbosity")
    parser.add_argument("-d", "--flaskdebug", action='store_true', help="Turn on Flask Debugging.")

    args = parser.parse_args()

    # Verbose Arguments
    VERBOSE = False
    VERBOSE = args.verbose

    # Flaskdebug global
    FLASKDEBUG = False
    FLASKDEBUG = args.flaskdebug

    FORMAT="%(levelname)s %(asctime)s %(name)s : %(message)s"

    if VERBOSE == True :
        logging.basicConfig(level=logging.DEBUG,
                            format=FORMAT)
        # URLLib3 is too verbose!
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    else :
        logging.basicConfig(level=logging.ERROR,
                            format=FORMAT)
        logging.getLogger("pika").setLevel(logging.WARNING)
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)


    LOGGER=logging.getLogger("snaggy")

    LOGGER.debug("Welcome to snaggy.")

    # Config File
    CONFIG=args.config

def run_http(flaskdebug=False, configfile="snaggy.ini") :

    '''
    This should istantiate the api server and the things needed.
    '''

    # Get the configuration file
    config_dictionary = readconfig.read_config(configfile=configfile)

    app = flask.Flask(__name__)

    # Make url/ vs. url the same thing
    app.url_map.strict_slashes = False

    snaggy_logger = logging.getLogger("snaggyhttp")

    ## UI Defaults
    api_context_root = config_dictionary["flask"].get("api_context_root", "/api")
    ui_context_root = config_dictionary["flask"].get("ui_context_root", "/ui")

    server_port = config_dictionary["flask"].get("port", 8080)

    bind_address = config_dictionary["flask"].get("bind_address", "::1")



    @app.before_first_request
    def before_first_request():
        snaggy_logger.debug("Welcome to Snaggy HTTP Server.")

    @app.before_request
    def before_request():
        #  Take the Bits
        flask.g.snaggy_logger = copy.copy(snaggy_logger)

        flask.g.config_items = config_dictionary

        try :

            db_conn = pymysql.connect(host=flask.g.config_items["db"]["dbhostname"], \
                        port=int(flask.g.config_items["db"]["dbport"]), \
                        user=flask.g.config_items["db"]["dbuser"], \
                        passwd=flask.g.config_items["db"]["dbpassword"], \
                        db=flask.g.config_items["db"]["dbname"], \
                        autocommit=flask.g.config_items["db"].get("autocommit", True) )

            flask.g.db = db_conn

        except Exception as e :
                flask.g.snaggy_logger.critical("Error connecting to database: {}".format(e))
                flask.abort(503)

        flask.g.cur = flask.g.db.cursor(pymysql.cursors.DictCursor)

        # Auth Workflow Here
        try:
            auth_header = flask.request.headers.get("Authorization")
            uname_pass_64 = auth_header.split()[1]
            decoded_uname_pass = base64.b64decode(uname_pass_64).decode("utf-8")
            flask.g.username = decoded_uname_pass.split(":")[0]
            password = "".join(decoded_uname_pass.split(":")[1:])

            # Get IP. If behind a proxy use the 'X-Forwarded-For' header if not,
            # fallback to the remote_addr thing.
            flask.g.ip = flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr)

        except Exception as e :
            # Unable to Get neccessary parts to authorize
            # Do a Basic Auth Request Here and Retry (ideally)
            flask.g.snaggy_logger.debug("Error reading Basic Auth Header: {}".format(str(e)))
            return flask.Response('Could not verify your access level for that URL.\n You have to login with proper credentials', \
                                    401, \
                                    {'WWW-Authenticate': 'Basic realm="Login Required"'} )
        else :
            verify_result = verify_password.verify_password(flask.g.username, password, \
                                                            flask.g.ip, flask.g.cur, flask.g.snaggy_logger)

            if verify_result[0] == True :
                flask.g.passinfo = verify_result[1]
            else:
                # Bad Password
                flask.abort(401)
        finally:
            pass

    @app.after_request
    def after_request(response):
        return response

    @app.teardown_request
    def teardown_request(response):
        # Get Rid of My DB Connection
        cur = getattr(flask.g, 'cur', None)
        if cur is not None:
            cur.close()
            db = getattr(flask.g, 'db', None)
        if db is not None:
            db.close()

        return response

    # Do API Imports Here
    from api import getarticle

    # Do UI Imports Here

    # Do API Registers Here
    app.register_blueprint(getarticle.getarticle, url_prefix=api_context_root)

    # Do UI Registers Here

    @app.route("/")
    def index():
        # Index
        return flask.render_template("index.html.jinja")

    app.run(debug=flaskdebug, port=server_port, threaded=True, host=bind_address)

if __name__ == "__main__" :

    run_http(flaskdebug=FLASKDEBUG, configfile=CONFIG)

