from flask import Flask, render_template, url_for, flash, redirect, request,send_file
from forms import RegistrationForm, LoginForm, ShareForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///database.db'
db=SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

mapped = db.Table('mapping',
    db.Column('user_id',db.Integer,db.ForeignKey('user.user_id')),
    db.Column('file_id',db.String(80),db.ForeignKey('files.id'))
)

class User(UserMixin,db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(80))
    mapping = db.relationship('Files',secondary=mapped, backref = db.backref('mapping',lazy='dynamic'))
    def get_id(self):
           return (self.user_id)
    def is_authenticated(self):
        return True


class Files(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)
    

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',current_user=current_user)


@app.route("/about")
def about():
    return render_template('about.html', title='About',current_user=current_user)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=generate_password_hash(form.password.data,method='sha256')
        new_user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form,current_user=current_user)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user,remember=form.remember.data)
                return redirect(url_for('account'))
        return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)


def getdata(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    return user.mapping

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account',current_user=current_user, data = getdata(current_user.user_id))

@app.route("/upload",methods=['POST'])
def upload():
    userid = request.args.get("userid")
    current_user = User.query.filter_by(user_id=userid).first()
    file = request.files['asprise_scans']            # add tag of file here
    filename = request.form.get("filename")
    newFile = Files(name=filename,data=file.read())
    db.session.add(newFile)
    newFile.mapping.append(current_user)
    db.session.commit()
    # return render_template('account.html', title='Account',current_user=current_user, data = getdata(current_user.user_id))
    return "Upload Success. Please reload the page."

@app.route("/share/<int:file_id>",methods=['GET','POST'])
@login_required
def share(file_id):                #assuming file_id is given
    file = Files.query.filter_by(id=file_id).first()
    # form = dict()
    # form['recipient_email'] = []
    # form['body'] = request.form['message']
    # form['subject'] = request.form['subject']
    # t = request.form['email'].replace(' ','')
    # form['recipient_email'] = t.split(',') 
    # print(form)
    # mail_func(form,file.data)
    form_data = ShareForm()
    if form_data.validate_on_submit():
        form = dict()
        form['recipient_email'] = []
        form['body'] = form_data.message.data
        form['subject'] = form_data.subject.data
        t1 = form_data.email.data
        t = t1.replace(' ','')
        form['recipient_email'] = t.split(',')
        for emailid in form['recipient_email'] :
            user = User.query.filter_by(email = emailid).first()
            print(type(user))
            if user is not None:
                file.mapping.append(user)
                db.session.commit()
        print(form)
        mail_func(form,file.data)
        return redirect(url_for('login'))
    
    return render_template('share.html', title='SHARE',current_user=current_user, data = getdata(current_user.user_id), form_data=form_data)

@app.route("/download/<int:file_id>")
def download(file_id):
    file_data = Files.query.filter_by(id=file_id).first()
    return send_file(BytesIO(file_data.data), attachment_filename = file_data.name, as_attachment=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def mail_func(form, file_name):
    import smtplib
    import datetime

    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders


    now = datetime.datetime.now()

    email_user = ''
    email_password = ''
    email_send = form['recipient_email']
    subject = form['subject']

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = ", ".join(email_send)
    msg['Subject'] = subject

    body = 'Sent by ' + '\n' + now.strftime("%Y-%m-%d %H:%M") + '\n' + form['body']
    msg.attach(MIMEText(body,'plain'))
    

    part = MIMEBase('application','octet-stream')
    part.set_payload(file_name)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= Document.pdf")

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_password)

    server.sendmail(email_user, email_send , text)
    server.quit()
if __name__ == '__main__':        
    app.run(host="0.0.0.0")
