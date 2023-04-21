from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    
    submit = SubmitField('Let me in!')
