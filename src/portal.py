from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'h7h77g7'
db = SQLAlchemy(app)

mapping = db.Table('mapping',
    db.Column('username',db.String(80),db.ForeignKey('user.username')),
    db.Column('id',db.Integer,db.ForeignKey('files.id'))
)

class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(80),unique=True,nullable=False)
    password = db.Column(db.String(80),nullable=False) 

class Files(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)
    

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@app.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/account")
def account():
    return render_template('account.html', title='Account')
if __name__ == '__main__':
    app.run(debug=True)