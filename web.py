#!flask/bin/python
import argparse
from functools import wraps

from flask import Flask, jsonify, g, redirect, url_for, session, send_from_directory
from flask_login import LoginManager, login_user
from flask_oauth2_login import GoogleLogin

from budget.aggregator import Aggregator
from budget.config import Config
from budget.database import *


def parse_arguments():
    # Parse command line arguments
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--config",
        required=True,
        help="Configuration path or S3 URL",
    )
    args_parser.add_argument(
        "--debug",
        help="Increase verbosity",
        action="store_true"
    )
    args_parser.add_argument(
        "--user-email",
        help="Pre-authenticated user e-mail",
    )
    return args_parser.parse_args()


app = Flask(__name__, static_url_path='/static')

args = parse_arguments()

config = Config(args.config)
db = Database(config.get_database_uri())
aggregator = Aggregator(db)

if args.user_email:
    config.pre_authenticated_user = args.user_email

google_client_id, google_client_secret = config.get_google_auth_credentials()

app.config.update(
    SECRET_KEY=google_client_secret,
    GOOGLE_LOGIN_REDIRECT_SCHEME="https",
    GOOGLE_LOGIN_CLIENT_ID=google_client_id,
    GOOGLE_LOGIN_CLIENT_SECRET=google_client_secret
)

login_manager = LoginManager(app)
google_login = GoogleLogin(app)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(google_login.authorization_url())
        return f(*args, **kwargs)

    return decorated_function


@app.before_request
def before_request():
    if app.debug and config.pre_authenticated_user:
        user = load_user(email=config.pre_authenticated_user)
    elif session.get("user_id"):
        user = load_user(email=session["user_id"])
    else:
        user = None
    g.user = user


@login_manager.user_loader
def load_user(email):
    return config.get_user_by_email(email)


@app.route("/")
@login_required
def index():
    return app.send_static_file('index.html')


@google_login.login_success
def login_success(token, profile):
    user = load_user(profile["email"])
    if user is not None:
        login_user(user, remember=True)
    return redirect(url_for("index"))


@google_login.login_failure
def login_failure(e):
    return jsonify(error=str(e))


@app.route("/api/v1.0/expenses/this_month")
@login_required
def get_expenses_for_this_month():
    result = aggregator.get_expenses_for_this_month(person=g.user)
    return jsonify(result)


@app.route("/api/v1.0/expenses/<year_and_month>")
@login_required
def get_expenses(year_and_month):
    try:
        year, month = [int(i) for i in year_and_month.split('-', 1)]
    except ValueError:
        raise InvalidUsage(message="Invalid date", status_code=400)
    result = aggregator.get_expenses_for_month(person=g.user, year=year, month=month)
    return jsonify(result)

if __name__ == "__main__":
    host = '0.0.0.0' if not args.debug else '127.0.0.1'
    app.run(host=host, debug=args.debug)
