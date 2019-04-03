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
    recipient_email = FieldList(StringField('RecipientEmail',validators=[DataRequired(),Email()]),min_entries=1)
    subject = StringField('Subject', validators=[DataRequired()])
    sender_name= StringField('SenderName', validators=[DataRequired()])
    body = StringField('Body')