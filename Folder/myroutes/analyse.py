import logging
from Folder import app
from datetime import date
from flask import render_template, redirect, url_for, flash
import Folder.global_vars

from Folder.myroutes.analyse_support import *


@app.route('/analyse', methods=["GET", "POST"])
def analyse():
    """
    Control logic for the flightrecord html view.
    Uses scan logic to assemble tug-glider flight pairs from the flights database.
    Presumes that all flight detail editing will be done in the "flights" view.
    :return: data to template "flightrecord.html"
    """
    ###- Check that start date is set

    if Folder.global_vars.start_date is None:
        flash(" You must set a date")
        return redirect(url_for('index'))
    my_tows = []
    unknown_tow = []
    no_height = []
    sheet_number: int = 0

    get_date = Folder.global_vars.start_date
    dt_get_date = date.fromisoformat(get_date)


    # get all flights for the chose day

    all_flights = Web_flights.query.filter(Web_flights.to_date == dt_get_date).order_by(Web_flights.flt_id).all()

    if all_flights:
        sheet_number = str(all_flights[0].sheet_number)

    data_frame, no_height, unknown_tows = build_tow_pairs(all_flights)

    # if there are no remaining un-filled data

    if data_frame and not unknown_tow and len(no_height) == 0:
        result = load_flightsheets(data_frame)  # save a csv version of the dataframe

    elif unknown_tow or no_height:  # otherwise abandon analysis and go back to webflights for repair
        if unknown_tow:
            logging.error(f"Unknown Tows: {unknown_tow}")
            flash(f" There are still unknown tows: {unknown_tow}")
        if no_height:
            logging.error(f"Unknown Launch Height: {no_height}")
            flash(f" There are still unknown launch height: {no_height}")
        return redirect(url_for('webflights'))

    return render_template('displayflight.html', flt_data=data_frame, sheet=sheet_number, to_date=get_date)


@app.route('/save_flightsheet')
def save_flightsheet():
    print("found POST")
    transfer_flightsheet()
    print(" SAV FLIGHTSHEET")
    return redirect(url_for('analyse'))
