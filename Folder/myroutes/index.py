from datetime import datetime, date
import logging
from flask import render_template, request, flash, redirect, url_for
from Folder import app, db
from Folder.models import Web_flights, Ktrax, Sheets
import Folder.global_vars

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


@app.route('/', methods=['GET', 'POST'])
def index():
    """ Main page
    Sets start and end dates
    Used to initiate Ktrax upload
    Used to initiate Wave Accounting formatted upload

    :return: Active start and end dates
    """
    if request.method != 'POST':
        return render_template('index.html')
    
    _start_date = request.form.get('start_date')
    if not _start_date:
        flash(' Must enter a start date')
        return redirect(url_for('index'))
    
    Folder.global_vars.start_date = _start_date
    dt_start_date = date.fromisoformat(_start_date)
    short_date = dt_start_date.strftime("%Y%m%d")
    
    Folder.global_vars.end_date = request.form.get('end_date')
    print(f'End Date {Folder.global_vars.end_date}')
    if Folder.global_vars.end_date:
        dt_end_date = date.fromisoformat(Folder.global_vars.end_date)
        short_end_date = dt_end_date.strftime("%Y%m%d")
    
    _sheet_id = request.form.get('sheet_id')
    if _sheet_id:
        _sheet = int(_sheet_id)
        print(f'Inval : {_sheet}')
        result = Sheets.query.filter(Sheets.flying_day == _start_date).first()
        if not result:
            new_sheet = Sheets(int(_sheet_id), _start_date)
            db.session.add(new_sheet)
            db.session.commit()
    
    if request.form.get('ktrax'):
        print('Checkbox')
        import_Ktraxdb()
    
    return render_template('index.html', start_date=Folder.global_vars.start_date,
                           end_date=Folder.global_vars.end_date)


# ============== Support functions =============


def import_Ktraxdb():
    """Import Ktrax data from a stored Ktrax database table
    and store in Webflights database table
    :return: Data transferred to a Webflights database
    """
    all_ktrax = Ktrax.query.all()
    existing_seq_nums = set(Web_flights.query.with_entities(Web_flights.seq_num).all())

    for row in all_ktrax:
        my_rego = rego3(row.glider)
        duplicate_flight = row.seq_num in existing_seq_nums
        new_row = (row.to_time, row.ld_time, my_rego, '', '', '', row.height, '')
        print("new row", new_row)
        to_date = datetime.strftime(row.to_time, '%Y-%m-%d')
        flt_class = map_rego_to_flt_class(my_rego)
        bill_status = map_rego_to_bill_status(my_rego)

        if not duplicate_flight:
            my_webdata = Web_flights(row.seq_num, row.flt_id, flt_class, to_date, row.to_time,
                                     row.ld_time, 0, my_rego, None, None,
                                     row.height, None, bill_status, 999, 0.0, None, None)
            db.session.add(my_webdata)

    db.session.commit()
    print("Flights added")

    return True


# ============== Utility functions =============

def check_duplicate_webflights(check_data) -> bool:
    """Check for pre existing record in the Webflights table to prevent inserting a duplicate record

    :param check_data: this is the "seq_num" data element to be checked
    :return:  Bool true / False to indicate duplicate
    """
    try:
        record = Web_flights.query.filter_by(seq_num=check_data).first()
        return record is not None
    except Exception as e:
        print("Error occurred:", str(e))
        return False


def rego3(instr: str) -> str:
    """ Return a three letter registration set from possible VH- style

    :param instr: Input call sign
    :return:  three letter true call sign
    """
    if instr is None:
        return ''
    elif len(instr) > 3:
        return instr[-3:]
    else:
        return instr[:3]
