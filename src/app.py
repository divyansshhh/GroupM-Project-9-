# import os
# import flask
# import requests
# from googleapiclient.discovery import build
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# import googleapiclient.discovery
# import os


# GOOGLE_APPLICATION_CREDENTIALS = "client_secret.json"

# SCOPES = ['https://mail.google.com/']

# app = flask.Flask(__name__)

# app.secret_key = 'T7ob_-0j-dsp1pyDdt79HhbV'


# @app.route('/')
# def index():
#   return flask.render_template('login.html')

# @app.route('/authorize')
# def authorize():
#   # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
#   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#      GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)

#   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

#   authorization_url, state = flow.authorization_url(
#       # Enable offline access so that you can refresh an access token without
#       # re-prompting the user for permission. Recommended for web server apps.
#       access_type='offline',
#       include_granted_scopes='true')

#   # Store the state so the callback can verify the auth server response.
#   flask.session['state'] = state

#   return flask.redirect(authorization_url)


# @app.route('/oauth2callback')
# def oauth2callback():
#   # Specify the state when creating the flow in the callback so that it can
#   # verified in the authorization server response.
#   state = flask.session['state']

#   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#       GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES, state=state)
#   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

#   # Use the authorization server's response to fetch the OAuth 2.0 tokens.
#   authorization_response = flask.request.url
#   flow.fetch_token(authorization_response=authorization_response)

#   # Store credentials in the session.
#   # ACTION ITEM: In a production app, you likely want to save these
#   #              credentials in a persistent database instead.
#   credentials = flow.credentials
#   flask.session['credentials'] = credentials_to_dict(credentials)
#   return flask.redirect(flask.url_for('home'))


# @app.route('/home')
# def home():
#     service = build('gmail', 'v1',flask.session['credentials'])
#     results = service.users().getProfile(userId='me').execute()
#     print(results)
#     return flask.render_template('home.html')


# def credentials_to_dict(credentials):
#   return {'token': credentials.token,
#           'refresh_token': credentials.refresh_token,
#           'token_uri': credentials.token_uri,
#           'client_id': credentials.client_id,
#           'client_secret': credentials.client_secret,
#           'scopes': credentials.scopes}



# if __name__ == '__main__':
#   # When running locally, disable OAuthlib's HTTPs verification.
#   # ACTION ITEM for developers:
#   #     When running in production *do not* leave this option enabled.
#   os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#   # Specify a hostname and port that are set as a valid redirect URI
#   # for your API project in the Google API Console.
#   app.run(debug=True)



import os
import json
import datetime

from flask import Flask, url_for, redirect, \
    render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, \
    logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError

basedir = os.path.abspath(os.path.dirname(__file__))

"""App Configuration"""

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('897595546518-0n1d7rjdc7hih7uo0i302sqef3vqfn65.apps.googleusercontent.com')
    CLIENT_SECRET = 'T7ob_-0j-dsp1pyDdt79HhbV'
    REDIRECT_URI = 'http://127.0.0.1:5000/oauth2callback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']


class Config:
    """Base config"""
    APP_NAME = "Test Google Login"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "somethingsecret"


class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test.db")


class ProdConfig(Config):
    """Production config"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "prod.db")


config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}

"""APP creation and configuration"""
app = Flask(__name__)
app.config.from_object(config['dev'])
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

""" DB Models """


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
""" OAuth Session creation """


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)


@app.route('/oauth2callback')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            print(user.email)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if  __name__ == "__main__":
    app.run(debug=True)