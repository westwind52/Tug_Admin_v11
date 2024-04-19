from flask import render_template, request, redirect, url_for, flash
import Folder.global_vars
from Folder import app
from Folder.models import Sheets
from Folder.myroutes.analyse_support import *


# logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

@app.route('/sheet_log', methods=['GET', 'POST'])
def sheet_log():
    _sheet_id = 0
    if request.method == 'GET':

        get_date = Folder.global_vars.start_date

        if get_sheet := Sheets.query.filter(
            Sheets.flying_day == Folder.global_vars.start_date
        ).first():
            _sheet_id = get_sheet.sheet_id
            str_sheet = str(_sheet_id)
            # print(f"get sheet {_sheet_id}")
            all_flights = Web_flights.query.filter(Web_flights.sheet_number == _sheet_id).all()
            if len(all_flights) > 0:
                my_data = []
                for row in all_flights:
                    data = (row.id, row.to_time, row.aircraft, row.flt_class)
                    my_data.append(data)

                tow_count = 1
                # print(f"Got Sheets {_sheet_id} {len(all_flights)}")
                my_tows = []
                unknown_tows = []
                for line in my_data:
                    if line[2] in Folder.global_vars.self_launch:
                        pass
                    elif line[2] in Folder.global_vars.tugs:
                        my_tows, unknown_tows, tow_count = find_glider_id(my_data, line, my_tows, unknown_tows, tow_count)

                data_frame = []
                no_height = []

                for tow in my_tows:
                    this_tow = load_flightsheet_frame(tow)
                    if this_tow.billed_ht == 0:
                        no_height.append(tow[1])
                    data_frame.append(this_tow)

                if data_frame and not unknown_tows and not no_height:
                    result = load_flightsheets(data_frame)
                elif len(unknown_tows) > 0 or len(no_height) > 0:
                    if unknown_tows:
                        # print(f" STOP -- Unknown Tows: {unknown_tow}")
                        flash(f" There are still unknown tows: {unknown_tows}")
                    if no_height:
                        # print(f" STOP -- Unknown Launch Height: {no_height}")
                        flash(f" There are still unknown launch height: {no_height}")
                    return redirect(url_for('webflights'))

                return render_template('flight_sheet.html', flt_data=data_frame, sheet=str_sheet, to_date=get_date)

        else:
            flash(' No sheet id')
            # -- Quit if no sheet entered for that day
            return redirect(url_for('webflights'))

        return redirect(url_for('webflights'))
