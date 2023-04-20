from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class AddGameForm(FlaskForm):
    steam_id = IntegerField('Game id on Steam', validators=[DataRequired()])
    status = IntegerField('How is it now?', validators=[DataRequired()])
    submit = SubmitField('Submit')
