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
    args = args_parser.parse_args()
    return args

args = parse_arguments()

config = Config(args.config)
db = Database(config.get_database_uri())
aggregator = Aggregator(db)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(google_login.authorization_url())
        return f(*args, **kwargs)
    return decorated_function

GOOGLE_LOGIN_CLIENT_ID, GOOGLE_LOGIN_CLIENT_SECRET = config.get_google_auth_credentials()

app = Flask(__name__, static_url_path='/static')
app.config.update(
  SECRET_KEY=GOOGLE_LOGIN_CLIENT_SECRET,
  GOOGLE_LOGIN_REDIRECT_SCHEME="http",
  GOOGLE_LOGIN_CLIENT_ID=GOOGLE_LOGIN_CLIENT_ID,
  GOOGLE_LOGIN_CLIENT_SECRET=GOOGLE_LOGIN_CLIENT_SECRET
)

google_login = GoogleLogin(app)

login_manager = LoginManager(app)

@app.before_request
def before_request():
    if session.get("user_id"):
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
def get_expenses_for_last_three_months():
    result = aggregator.get_expenses_for_this_month(person=g.user)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=args.debug)