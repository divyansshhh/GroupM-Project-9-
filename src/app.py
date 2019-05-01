from flask import Flask, render_template, url_for, flash, redirect, request, send_file
from forms import RegistrationForm, LoginForm, ShareForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from io import BytesIO
import os
import flask
import requests
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os
import send_email


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

GOOGLE_APPLICATION_CREDENTIALS = "client_secret.json"

SCOPES = ['https://mail.google.com/']

app.secret_key = 'T7ob_-0j-dsp1pyDdt79HhbV'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


mapped = db.Table('mapping',
                  db.Column('user_id', db.Integer,
                            db.ForeignKey('user.user_id')),
                  db.Column('file_id', db.String(80),
                            db.ForeignKey('files.id'))
                  )


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    mapping = db.relationship(
        'Files', secondary=mapped, backref=db.backref('mapping', lazy='dynamic'))

    def get_id(self):
        return (self.user_id)

    def is_authenticated(self):
        return True


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', current_user=current_user)


@app.route("/about")
def about():
    return render_template('about.html', title='About', current_user=current_user)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, current_user=current_user)


@app.route("/login", methods=['GET', 'POST'])
def login():

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(

        access_type='offline',
        include_granted_scopes='true')

    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():

    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    service = build('gmail', 'v1', credentials=credentials)
    results = service.users().getProfile(userId='me').execute()
    print(results)
    user = User.query.filter_by(email=results['emailAddress']).first()
    if user:
        login_user(user)
    else:
        new_user = User(username="test",
                        email=results['emailAddress'], password="password")
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.redirect(flask.url_for('account'))


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def getdata(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    return user.mapping


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account', current_user=current_user, data=getdata(current_user.user_id))


@app.route("/upload", methods=['POST'])
def upload():
    userid = request.args.get("userid")
    current_user = User.query.filter_by(user_id=userid).first()
    file = request.files['asprise_scans']            # add tag of file here
    filename = request.form.get("filename") + ".pdf"
    newFile = Files(name=filename, data=file.read())
    db.session.add(newFile)
    newFile.mapping.append(current_user)
    db.session.commit()
    # return render_template('account.html', title='Account',current_user=current_user, data = getdata(current_user.user_id))
    return "Upload Success. Please reload the page."


@app.route("/share/<int:file_id>", methods=['GET', 'POST'])
@login_required
def share(file_id):  # assuming file_id is given
    file = Files.query.filter_by(id=file_id).first()
    form_data = ShareForm()
    if form_data.validate_on_submit():
        form = dict()
        form['recipient_email'] = []
        form['body'] = form_data.message.data
        form['subject'] = form_data.subject.data
        t1 = form_data.email.data
        t = t1.replace(' ', '')
        form['recipient_email'] = t.split(',')
        for emailid in form['recipient_email']:
            user = User.query.filter_by(email=emailid).first()
            print(type(user))
            if user is not None:
                file.mapping.append(user)
                db.session.commit()

        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])
        service = build('gmail', 'v1', credentials=credentials)
        sendInst = send_email.send_email(service)
        message = sendInst.create_message_with_attachment(form, file.data)
        print(sendInst.send_message('me', message))

    return render_template('share.html', title='SHARE', current_user=current_user, data=getdata(current_user.user_id), form_data=form_data)


@app.route("/download/<int:file_id>")
def download(file_id):
    file_data = Files.query.filter_by(id=file_id).first()
    return send_file(BytesIO(file_data.data), attachment_filename=file_data.name, as_attachment=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True)
