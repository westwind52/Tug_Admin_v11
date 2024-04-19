from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, validators

class Tug_Form(FlaskForm):

    registration = StringField('registration' )
    take_off_datetime = DateTimeField(label='Take Off Date Time')
    submit = SubmitField('Submit')

