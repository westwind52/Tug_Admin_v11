import logging

from flask_wtf import FlaskForm
from wtforms import FileField, StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, AnyOf, Length, DataRequired
from flask import render_template, request, redirect, url_for, flash

from Folder import app, db
from Folder.myroutes.my_utils import *

class Aircraft_UpdateForm(FlaskForm):

    sheet_number = IntegerField( 'Sheet_Number' )
    flt_class = StringField( label='Flight Category (CLUB, GLIDER)', validators=[AnyOf(["CLUB", "GLIDER"])])
    to_date = StringField('Date')
    to_time = StringField('TakeOff (hh:mm)')
    ld_time = StringField('Landing (hh:mm)')
    aircraft = StringField('Registration', validators=[DataRequired(), Length(min=3, max=3) ])
    OGN_ht = IntegerField('OGN Receiver Height')
    launch_ht = IntegerField('Billed Launch Height')
    pilot_initials = StringField( 'Pilot Initials (2)', validators=[DataRequired(), Length(min=2, max=2)] )
    heavy = StringField('Heavy? (Y/N)', validators=[DataRequired(), AnyOf(["Y", "N"], message="Either 'Y' or 'N'" )])

@app.route('/tug_update/<int:_id>', methods=['GET'])
def tug_update(_id: int):
    """ Main workhorse page
    Pops as a modal on the Webflights page
    Used to edit / add / correct flight data - mostly set launch height


    """
    flt_form = Aircraft_UpdateForm()
    my_data = Web_flights.query.get(_id)
    load_tug_form_data(flt_form, my_data)


@app.route('/tug_update/<int:_id>', methods=['POST'])
def tug_update(_id: int):
    """ Main workhorse page
    Used to add / correct flight data - mostly set launch height
    :param: _id: int for flight record ident
    :return: Edited flight record stored in DATABASE
    """
    my_data = Web_flights.query.get(_id)
    _str_to_time = request.form['to_time']
    my_data.to_time = dt_combine(my_data.to_date, _str_to_time)
    str_ld_time = request.form['ld_time']
    if str_ld_time != None and str_ld_time != '':
        my_data.ld_time = dt_combine(my_data.to_date, str_ld_time)
        flt_timedelta = my_data.ld_time - my_data.to_time
        my_data.flt_time = int(flt_timedelta.total_seconds() / 60)
    my_data.flt_id = make_id(my_data.to_date, _str_to_time)
    my_data.aircraft = request.form['aircraft']
    my_data.OGN_ht = request.form['OGN_ht']
    my_data.launch_ht = request.form['launch_ht']
    my_data.sheet_number = request.form['sheet_number']

    db.session.commit()
    flash("Towplane Flight Updated Successfully")
    return redirect(url_for('webflights'))

def load_tug_form_data(flt_form, my_data):
    if request.method == 'GET':

        flt_form.sheet_number.data = my_data.sheet_number
        flt_form.flt_class.data = my_data.flt_class
        flt_form.to_date.data = my_data.to_date
        if my_data.to_time is not None:
            str_to_time = my_data.to_time.strftime("%H:%M")
        else:
            str_to_time = ''
        flt_form.to_time.data = str_to_time

        if my_data.ld_time is not None:
            str_ld_time = my_data.ld_time.strftime("%H:%M")
        else:
            str_ld_time = ''
        flt_form.ld_time.data = str_ld_time
        flt_form.aircraft.data = my_data.aircraft
        flt_form.pilot_initials = my_data.pilot_initials
        flt_form.heavy = my_data.heavy
        flt_form.OGN_ht.data = my_data.OGN_ht
        flt_form.launch_ht.data = my_data.launch_ht

    return render_template('tug_update.html', form = flt_form)

@app.route('/glider_update/<int:_id>', methods=['GET', 'POST'])
def glider_update(_id):
    """ Main workhorse page
    Pops as a modal on the Webflights page
    Used to edit / add / correct flight data - mostly set launch height

    :return: Edited flight record stored in DATABASE
    """
    fltform1 = Aircraft_UpdateForm()
    my_data = Web_flights.query.get(_id)

    if request.method == 'GET':

        fltform1.sheet_number.data = my_data.sheet_number
        fltform1.flt_class.data = my_data.flt_class
        fltform1.to_date.data =  my_data.to_date

        if my_data.to_time is not None:
            str_to_time = my_data.to_time.strftime("%H:%M")
        else:
            str_to_time = ''
        fltform1.to_time.data = str_to_time

        if my_data.ld_time is not None:
            str_ld_time = my_data.ld_time.strftime("%H:%M")
        else:
            str_ld_time = ''
        fltform1.ld_time.data = str_ld_time

        fltform1.aircraft.data = my_data.aircraft
        fltform1.pilot_initials.data = my_data.pilot_initials

        if my_data.heavy:
            fltform1.heavy.data = 'Y'
        else:
            fltform1.heavy.data = 'N'

    if request.method == 'POST':

        _str_to_time = request.form['to_time']
        my_data.to_time = dt_combine(my_data.to_date, _str_to_time)
        str_ld_time = request.form['ld_time']
        if str_ld_time != None and str_ld_time != '':
            my_data.ld_time = dt_combine(my_data.to_date, str_ld_time)
            flt_timedelta = my_data.ld_time - my_data.to_time
            my_data.flt_time = int(flt_timedelta.total_seconds() / 60)
        my_data.flt_id = make_id(my_data.to_date, _str_to_time)
        my_data.aircraft = request.form['aircraft']
        my_data.pilot_initials = request.form['pilot_initials']
        record = get_pilot_object(my_data.pilot_initials)
        if record is not None:
            my_data.pilot_id = record.id
        else:
            my_data.pilot_id = None

        return_value = request.form['heavy']
        my_data.heavy = True if return_value == "Y" else False
        my_data.sheet_number = request.form['sheet_number']


        db.session.commit()
        flash("Glider Flight Updated Successfully")
        return redirect(url_for('webflights'))

    return render_template('glider_update.html', form=fltform1)
