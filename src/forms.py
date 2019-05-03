from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FieldList
from wtforms.validators import DataRequired, Length, Email, EqualTo




class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ShareForm(FlaskForm):
    email = StringField('Recipient',validators=[DataRequired()])
    subject = StringField('Subject',validators=[DataRequired()])
    message = StringField('Message',validators=[DataRequired()])
    send = SubmitField('Send')
    
class NameForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    send = SubmitField('Send')