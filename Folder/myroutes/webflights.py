from typing import List

from flask import render_template, request, redirect, url_for, flash
import random

from sqlalchemy.exc import SQLAlchemyError

import Folder.global_vars
from Folder.myroutes.sheet_log import *
from Folder.myroutes.analyse_support import *

from Folder.myroutes.flight_update import Aircraft_UpdateForm
from Folder.myroutes.tug import Tug_Form

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


@app.route('/webflights')
def webflights():
    """Main editing and management page for flight data.
    Uses data uploaded from KTRAX via the KTRAX import functions triggered from Index page
    Data stored in the Webflights database table. Main place for edit dat and adding flights not
    captured in KTRAX.
    :return:
    """
    idents = []
    data_frame: list[tuple] = []
    unknown_height = []
    sheet_id = 998

    if Folder.global_vars.start_date is None:
        Folder.global_vars.start_date = datetime.today()
    start = Folder.global_vars.start_date

    sheet_data = Sheets.query.filter(Sheets.flying_day == start).first()
    if sheet_data:
        sheet_id = sheet_data.sheet_id

    if not Folder.global_vars.acft:
        ac_records = Aircraft.query.all()

        for ac in ac_records:
            Folder.global_vars.acft.update({ac.registration: [ac.pilot_initials, ac.heavy]})

        logging.info(f"Aircraft :{Folder.global_vars.acft}")

    all_data = Web_flights.query.filter(Web_flights.to_date == start).order_by(Web_flights.flt_id).all()

    for flight in all_data:
        idents.append(flight.id)
        if flight.launch_ht == 0:
            unknown_height.append(flight.id)

    logging.debug(idents)
    unknowns = check_known_aircraft(idents)

    display_list = []
    for flight in all_data:
        # process the flight data into a flight "rec"  -record
        rec = process_flight(flight)
        rec["sheet_number"] = sheet_id
        # make the flight record as a tuple for transition to web page
        my_rec = make_flt_rec(rec)
        data_frame.append(my_rec)

    # --Check for unknown pilots, unallocated launch height and unverified data
    result, pilots, heights, unverified = audit_aircraft(data_frame)

    # -- find the tow pair matches and load the pair ids into the data base

    tows, unknowns = find_tow_matchs(all_data)
    if len(tows) > 0:
        load_tow_pairs(tows)

    if not result:
        if len(pilots) != 0:  # Still unknown pilots
            flash(f" Unknown pilots {pilots}")
        if len(heights) != 0:  # Still unallocaed launch height
            flash(f" Unknown heights {heights}")

    if len(unknowns) != 0:
        outstr = str(unknowns)
        flash(" Unknown aircraft " + outstr)
        logging.debug(" Unknown aircraft " + outstr)
    if len(unknown_height) != 0:
        outstr = str(unknown_height)
        flash(" Unknown height " + outstr)
        logging.debug(" Unknown height " + outstr)
    if len(unverified) != 0:
        outstr = str(unverified)
        flash(" Unverified " + outstr)

    # if there id flight data - go to web page

    if len(data_frame) > 0:
        return render_template('web_flights.html', flights=data_frame)
    else:
        flash(f" No data for this date: {start} ")
        return render_template('index.html')


@app.route('/webflight_insert/<int:_id>', methods=['GET', 'POST'])
def webflight_insert(_id):
    """Used to INSERT a new flight record in the main Webflights datatable
    :return: New RECORD stored in Webflights DATABASE table
    """

    flightForm = Aircraft_UpdateForm()
    my_data = Web_flights.query.get(_id)

    if request.method == 'GET':
        tug_seq_num = None
        flightForm.sheet_number.data = my_data.sheet_number
        flightForm.to_date.data = my_data.to_date
        if my_data.to_time is not None:
            str_to_time = my_data.to_time.strftime("%H:%M")
        else:
            str_to_time = ''
        flightForm.to_time.data = str_to_time

        tug_seq_num = my_data.seq_num

    if request.method == 'POST':
        if my_data.seq_num is None:
            seq_num = random.randint(120000000000, 900000000000)
        else:
            seq_num = my_data.seq_num + 1
        to_date = Folder.global_vars.start_date
        str_to_time = request.form['to_time']
        to_time = dt_combine(to_date, str_to_time)
        flt_id = int(make_id(to_date, str_to_time))

        str_ld_time = request.form['ld_time']
        if str_ld_time is not None and str_ld_time != '':
            ld_time = dt_combine(to_date, str_ld_time)
        else:
            ld_time = None

        flt_time = '0'
        aircraft = request.form['aircraft']
        pilot_initials = request.form['pilot_initials']
        return_value = request.form['heavy']
        heavy = return_value == "Y"

        cost = 0.0

        my_flight = Web_flights(seq_num, flt_id, my_data.flt_class, to_date, to_time, ld_time,
                                flt_time, aircraft, pilot_initials, heavy,
                                my_data.OGN_ht, my_data.launch_ht, my_data.bill_status, my_data.sheet_number, cost, _id,
                                None)
        db.session.add(my_flight)
        db.session.commit()
        flash('webflight inserted ')
        return redirect(url_for('webflights'))
    # if GET request
    return render_template('flight_insert.html', form=flightForm)


@app.route('/webflight_delete/<int:_id>', methods=['GET', 'POST'])
def webflight_delete(_id):
    """
    Delete one record 'flt_id'.  'flt_id' is not primary key
    :param _id is primary key
    :return: redirect
    """
    my_data = Web_flights.query.filter_by(id=_id).delete()
    # db.session.delete(my_data)
    db.session.commit()
    flash('Flight deleted')

    return redirect(url_for('webflights'))


@app.route('/webflight_verify/<int:_id>', methods=['GET'])
def webflight_verify(_id):
    my_data = Web_flights.query.filter_by(id=_id).first()
    my_data.bill_status = 'VERIFIED'
    db.session.commit()
    flash('Flight verified')

    return redirect(url_for('webflights'))


@app.route('/tug_add', methods=['GET', 'POST'])
def tug_add():
    form = Tug_Form()

    if request.method == 'POST':
        registration = request.form['registration']
        take_off = request.form['take_off_datetime']
        to_date = take_off[0:10]
        to_time = take_off[11:19]
        my_rego = registration
        dt_take_off = datetime.strptime(take_off, '%Y-%m-%d %H:%M:%S')
        short_date = dt_take_off.strftime("%Y%m%d")

        # print(f'Rego {registration} Date {short_date} DT {dt_take_off}  {to_date} {to_time}')

        if my_rego == 'PXI' or my_rego == 'TNE':
            flt_class = 'TUG'
            bill_status = "NOT BILLLED"
        else:
            flt_class = "VISITOR"
            bill_status = "#---#"

        seq_num = random.randint(120000000000, 900000000000)
        my_flt_id = make_id(to_date, to_time)
        int_flt_id = int(my_flt_id) - 1
        # flt_id = str(int_flt_id - 1)

        my_webdata = Web_flights(seq_num, int_flt_id, 'TUG', to_date, dt_take_off,
                                 dt_take_off, 0, my_rego, None, None,
                                 0, None, bill_status, 999, 0.0, None, None)
        db.session.add(my_webdata)
        db.session.commit()
        # print(f"Tow Flight added {to_time}")

        flash('Tug Add')
        return redirect(url_for('webflights'))
    return render_template('/tug.html', form=form)


# @app.route('/sheet_log/<int:_id>', methods=['GET','POST'])
# def asheet_log(_id):
#     all_data = Web_flights.query.filter(Web_flights.sheet_number ==_id).all()
#     #print(all_data)
#     # db.session.commit()
#     flash('sheet log')
#     #print("in Sheet Log")
#     return redirect(url_for('webflights'))
#     #return redirect(url_for('sheets'))

# =============== Utility

def find_tow_matchs(all_flights, self_launch, tugs):
    """
    Find tow matches in the given list of flights.

    Args:
        all_flights (list): List of flight objects.
        self_launch (list): List of self launch aircraft.
        tugs (list): List of tug aircraft.

    Returns:
        tuple: A tuple containing two lists - matched_tows and unknown_tows.
    """
    matched_tows = []
    unknown_tows = []
    no_height = []
    try:
        if len(all_flights) > 0:
            sheet_number = str(all_flights[0].sheet_number)
        flight_data = [(row.id, row.to_time, row.aircraft, row.flt_class) for row in all_flights]

        tow_count = 1
        my_data_dict = {}
        for line in flight_data:
            if line[2] in self_launch:
                pass
            elif line[2] in tugs:
                tow_id = line[0]
                if tow_id in my_data_dict:
                    result = my_data_dict[tow_id]
                    matched_tows.append((tow_count, tow_id, result,))
                    tow_count += 1
                else:
                    result = check_match(flight_data, tow_id, line[1])
                    my_data_dict[tow_id] = result
                    if result:
                        matched_tows.append((tow_count, tow_id, result,))
                        tow_count += 1
                    else:
                        unknown_tows.append(tow_id)
    except Exception as e:
        # Handle the exception here
        print(f"An error occurred: {e}")

    return matched_tows, unknown_tows


def load_tow_pairs(tows):
    tow_ids = [tow[1] for tow in tows]
    glider_ids = [tow[2] for tow in tows]
    tow_flights = Web_flights.query.filter(Web_flights.id.in_(tow_ids)).all()
    glider_flights = Web_flights.query.filter(Web_flights.id.in_(glider_ids)).all()
    
    for tow in tow_flights:
        tow.pair_id = next(tow_pair[2] for tow_pair in tows if tow_pair[1] == tow.id)
    for glider in glider_flights:
        glider.pair_id = next(tow_pair[1] for tow_pair in tows if tow_pair[2] == glider.id)
    
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        flash(f"Error occurred during database operation: {str(e)}")
        logging.error(f"Error occurred during database operation: {str(e)}")
    
    return
