from dataclasses import dataclass
import logging
from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, BooleanField, SubmitField, IntegerField, validators
from csv import DictReader
from Folder import app, db
from Folder.models import Aircraft


class Aircraft_Form(FlaskForm):

    registration = StringField( 'registration' )
    make = StringField( 'make' )
    self_launch = StringField('self_launch')
    pilot_initials = StringField( 'pilot_initials')
    normal_pilot = StringField('normal_pilot')
    acft_class = StringField('acft_class')
    heavy = StringField(label='heavy')
    #submit = SubmitField('Submit')


@app.route('/aircraft')
def aircraft():

    get_aircraft()
    all_acft = Aircraft.query.all()

    return render_template('aircraft.html', aircraft=all_acft)


@app.route('/aircraft_insert', methods=['GET', 'POST'])
def aircraft_insert():

    form = Aircraft_Form()
    if request.method == 'POST':
        registration = request.form['registration']
        make = request.form['make']
        pilot_initials = request.form['pilot_initials']
        normal_pilot = request.form['normal_pilot']
        acft_class = request.form['acft_class']
        return_value = request.form['heavy']
        heavy = True if (return_value == "y" or return_value == "Y") else False
        return_value = request.form['self_launch']
        self_launch = 1 if (return_value == "y" or return_value == "Y") else 0

        my_acft = Aircraft(registration, make, self_launch, pilot_initials, normal_pilot, acft_class, heavy)
        print(my_acft)
        db.session.add(my_acft)
        db.session.flush()
        db.session.commit()
        flash('glider inserted ')
        return redirect(url_for('aircraft', _external=True))

    return  render_template('aircraft_insert.html', form = form)


@app.route('/aircraft_update/<id>', methods=['GET', 'POST'])
def aircraft_update(id):
    my_data = Aircraft.query.get(id)
    form = Aircraft_Form()
    
    if request.method == 'POST':
        form.registration.data = my_data.registration
        form.make.data = my_data.make
        form.self_launch.data = convert_boolean_to_string(my_data.self_launch)
        form.pilot_initials.data = my_data.pilot_initials
        form.normal_pilot.data = my_data.normal_pilot
        form.acft_class.data = my_data.acft_class
        form.heavy.data = convert_boolean_to_string(my_data.heavy)

    if form.validate_on_submit():
        print(" In update --- 2")
        fields = ['registration', 'make', 'pilot_initials', 'acft_class', 'heavy', 'self_launch']
        for field in fields:
            value = request.form[field]
            if value != '':
                setattr(my_data, field, value)

        my_data.heavy = True if request.form['heavy'] == "Y" else False
        my_data.self_launch = True if request.form['self_launch'] == "Y" else False

        db.session.commit()

        flash("Glider Updated Successfully")
        return redirect(url_for('aircraft'))

    return "Invalid request method. Please use a POST request to update the aircraft."


@app.route('/aircraft/get_csv')
def get_csv() -> object:
    """

    :return: 
    """
    file_path = 'd:/DATA/aircraft.csv'  # Configurable file path

    try:
        with (open(file_path, newline='') as csvfile):
            all_acft = DictReader(csvfile)
            print("opened file")

            rows: list[Aircraft] = []

            for row in all_acft:
                row['self_launch'] = int(row['self_launch'])
                row['heavy'] = int(row['heavy'])
                my_data = Aircraft(row['registration'], row['make'], row['self_launch'],
                                   row['pilot_initials'], row['pilot'], row['acft_class'], row['heavy'])
                print(f"Mydata: {my_data}")
                rows.append(my_data)

            db.session.add_all(rows)
            db.session.commit()

    except (FileNotFoundError, PermissionError) as e:
        print(f"Error opening CSV file: {e}")

    return redirect(url_for('aircraft'))

@app.route('/aircraft_delete/<int:_id>', methods=['GET', 'POST'])
def aircraft_delete(_id):
    """
    Delete one record 'flt_id'.  'flt_id' is not primary key
    :param _id is primary key
    :return: redirect
    """
    if isinstance(_id, int) and _id > 0:
        try:
            aircraft = Aircraft.query.get(_id)
            if aircraft:
                logging.debug(f"Aircraft deleted: {_id}")
                db.session.delete(aircraft)
                try:
                    db.session.commit()
                    flash('Flight deleted')
                except Exception as e:
                    flash('Error committing changes to the database: ' + str(e))
            else:
                flash('Aircraft not found')
        except Exception as e:
            flash('Error deleting flight: ' + str(e))
    else:
        flash('Invalid aircraft ID')

    return redirect(url_for('aircraft'))

def get_aircraft():
    """
    Get all aircraft records from db table
    :return: my_data as all records
    """
    try:
        my_data = Aircraft.query.all()
    except Exception as e:
        # Handle the exception here
        print(f"Error occurred during database query: {str(e)}")
        my_data = []

    return my_data

@dataclass
class Form:
    registration: str
    make: str
    self_launch: bool
    pilot_initials: str
    normal_pilot: str
    acft_class: str
    heavy: bool

def make_form(data):
    """
    Create a form dictionary with relevant attributes from the given data.

    Args:
        data: An object containing the required attributes.

    Returns:
        A dictionary representing the form data.
    """
    try:
        out = {
            'registration': getattr(data, 'registration', None),
            'make': getattr(data, 'make', None),
            'self_launch': getattr(data, 'self_launch', None),
            'pilot_initials': getattr(data, 'pilot_initials', None),
            'normal_pilot': getattr(data, 'normal_pilot', None),
            'acft_class': getattr(data, 'acft_class', None),
            'heavy': getattr(data, 'heavy', None)
        }
    except Exception as e:
        # Handle the exception here
        out = {}
    return out
