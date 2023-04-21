from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class ReviewForm(FlaskForm):
    positive = BooleanField('Do you recommend it?')
    steam_id = IntegerField('Game id on Steam', validators=[DataRequired()])
    content = TextAreaField("Content ahead", validators=[DataRequired()])
    is_private = BooleanField("private?")
    
    submit = SubmitField('Submit')
