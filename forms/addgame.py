from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired


class AddGameForm(FlaskForm):
    status_list = ['in process', 'planning', 'done', 'postponed', 'quitted']

    steam_id = IntegerField('Game id on Steam', validators=[DataRequired()])
    status = SelectField('How is it now?', choices=[(i, v) for i, v in enumerate(status_list)],
                         validators=[DataRequired()])
    
    submit = SubmitField('Submit')
