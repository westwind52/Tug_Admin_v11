import csv
import logging
from collections import namedtuple
from datetime import datetime, time, timedelta

import Folder.global_vars
from Folder import db
from Folder.models import Web_flights, Uploads, Aircraft, Pilots, Flightsheets


# ======== Utility Functions ====================

def get_aircraft(rego):
    aircraft = Aircraft.query.filer_by(Aircraft.registration == rego).first()

    return aircraft


def audit_aircraft(my_data):
    unknown_pilots = []
    unallocated_height = []
    unverified = []

    for flight in my_data:
        if flight.flt_class == 'GLIDER' or flight.flt_class == 'CLUB':
            if flight.pilot_initials == 'UK' or flight.pilot_initials == '':
                unknown_pilots.append(flight.id)

        if flight.flt_class == 'TUG':
            if not flight.launch_ht:
                unallocated_height.append(flight.id)

        if flight.flt_class == 'CLUB' and flight.pilot_initials not in Folder.global_vars.bulk_bill:
            if flight.bill_status != 'VERIFIED':
                unverified.append(flight.id)

    if len(unknown_pilots) == 0 and len(unallocated_height) == 0 and len(unverified) == 0:
        result = True
    else:
        result = False
    return (result, unknown_pilots, unallocated_height, unverified)


def update_webflight(id, flt_var, flt_val):
    my_data = Web_flights.query.get(id)
    # print(my_data)
    my_data.flt_time = flt_val
    db.session.commit()
    my_data = Web_flights.query.get(id)
    # print(my_data)

    return


def get_pilot_object(initials: str):
    rec = Pilots.query.filter_by(pilot_initials=initials).first()
    if rec is not None:
        print(f"PILOT Found:{rec.pilot_initials, rec.pilot_name}")
    else:
        print(f"Pilot not found  {initials}")

    return rec


def make_id(my_date: str, my_time: str) -> str:
    """ Compose a 12 character string as YYYYMMDDHHMM

    :param my_date: date as string
    :param my_time: time as string
    :return: 12 character string, no delimiters
    """
    # print(f"MAKE ID --date: {my_date}  {type(my_date)}  time {my_time}  {type(my_time)}")

    d = datetime.fromisoformat(my_date)
    t = time.fromisoformat(my_time)
    dt = datetime.combine(d, t)
    str_flt_id = dt.strftime("%Y%m%d%H%M")
    return str_flt_id


def dt_combine(my_date: str, my_time: str) -> datetime:
    if my_date != None and my_time != None:

        d = datetime.fromisoformat(my_date)
        t = time.fromisoformat(my_time)
        dt = datetime.combine(d, t)
    else:
        dt = None

    return dt


def check_duplicate_uploads(check_data: int) -> bool:
    """Check for pre existing record in the Uploads table to prevent inserting a duplicate record

    :param check_data: this is the "seq_num" data element to be checked
    :return:  Bool true / False to indicate duplicate
    """
    my_count = Uploads.query.filter_by(seq_num=check_data).count()
    if my_count > 0:
        result = True
    else:
        result = False

    # print("Check duplicate", result)
    return result


def check_known_aircraft(idents: list[int]) -> set:
    '''Use pilot information pre-stored in Global variable 'acft'
    to complete the pilot and heavy class field in the webflights table if None

    returns: List of unknown aircraft
    '''

    unknowns = set()

    for _id in idents:

        my_data = Web_flights.query.get(_id)
        # check Null return
        if my_data != None:
            this_rego = my_data.aircraft
            if this_rego not in Folder.global_vars.tugs:
                if my_data.pilot_initials == None:
                    if this_rego in Folder.global_vars.acft.keys():
                        my_data.pilot_initials = Folder.global_vars.acft[this_rego][0]
                        db.session.commit()
                    else:
                        unknowns.add(this_rego)  # acft not found

                if my_data.heavy == None:
                    if this_rego in Folder.global_vars.acft.keys():
                        my_data.heavy = Folder.global_vars.acft[this_rego][1]
                        db.session.commit()

    return unknowns


def make_record(flight) -> dict:
    return {"id": flight.id,
            "seq_num": flight.seq_num,
            "flt_id": flight.flt_id,
            "flt_class": flight.flt_class,
            "to_date": flight.to_date,
            "to_time": flight.to_time,
            "ld_time": flight.ld_time,
            "flt_time": flight.flt_time,
            "aircraft": flight.aircraft,
            "pilot_initials": flight.pilot_initials,
            "heavy": flight.heavy,
            "OGN_ht": flight.OGN_ht,
            "launch_ht": flight.launch_ht,
            "bill_status": flight.bill_status,
            "sheet_number": flight.sheet_number,
            "cost": flight.cost}


def make_flt_rec(_rec) -> namedtuple:
    flight_record = namedtuple('flight_record', ['id', 'seq_num', 'flt_id', 'flt_class', 'to_date', 'to_time',
                                                 'ld_time', 'flt_time', 'aircraft', 'pilot_initials', 'heavy', 'OGN_ht',
                                                 'launch_ht', 'bill_status', 'sheet_number', 'cost'])

    out_rec = flight_record(_rec["id"],
                        _rec["seq_num"],
                        _rec["flt_id"],
                        _rec["flt_class"],
                        _rec["to_date"],
                        _rec["to_time"],
                        _rec["ld_time"],
                        _rec["flt_time"],
                        _rec["aircraft"],
                        _rec["pilot_initials"],
                        _rec["heavy"],
                        _rec["OGN_ht"],
                        _rec["launch_ht"],
                        _rec["bill_status"],
                        _rec["sheet_number"],
                        _rec["cost"], )
    return out_rec


def update_costs(ident, cost):
    #   User.query.filter_by(username == 'admin').update(dict(email='my_new_email@example.com')))
    rec = Web_flights.query.filter_by(id=ident).first()
    rec.cost = cost
    db.session.commit()


def update_tow_payee(ident, payee):
    #   User.query.filter_by(username == 'admin'.update(dict(email='my_new_email@example.com')))
    rec = Web_flights.query.filter_by(id=ident).first()
    rec.pilot_initials = payee
    db.session.commit()


def update_bill_status(ident: int, token: str):
    rec = Web_flights.query.filter_by(id=ident).first()
    rec.bill_status = token
    db.session.commit()


def transfer_flightsheet():
    """
    Transfer contents of a stored CSV one day flightsheet file to db table flight sheets
    :return:
    """
    h = bool
    db.session.query(Flightsheets).delete()
    db.session.commit()

    with open('sheets.csv', newline='') as csvfile:
        f = csv.DictReader(csvfile)
        for row in f:

            if row['heavy'] == 'True':
                row['heavy'] = True
            else:
                row['heavy'] = False

            dt_tow_date = datetime.fromisoformat(row['tow_date'])
            row['tow_date'] = dt_tow_date

            data = Flightsheets(**row)
            db.session.add(data)
            db.session.commit()
    return


def store_flightsheets(data):
    return


def load_flightsheets(data):
    """
    Write a 'flightsheets'  CSV file.
    Csv file written each time a data set is sent to analyse.
    :param data:
    :return:
    """

    with open('sheets.csv', 'w', newline='') as csvfile:
        fieldnames = ['sheet_id', 'tow_date', 'tow', 'payer', 'tug_id', 'glider_id', 'tug_to', 'tug_ld', 'gld_ld',
                      'ogn_ht', 'billed_ht', 'flt_time', 'heavy', 'tow_cost', 'glider_cost', 'billed']

        f = csv.DictWriter(csvfile, fieldnames=fieldnames)

        f.writeheader()
        for row in data:
            f.writerow({
                'sheet_id': 58,
                'tow_date': row.tow_date,
                'tow': row.tow,
                'payer': row.payer,
                'tug_id': row.tug_id,
                'glider_id': row.glider_id,
                'tug_to': row.tug_to,
                'tug_ld': row.tug_ld,
                'gld_ld': row.gld_ld,
                'ogn_ht': row.ogn_ht,
                'billed_ht': row.billed_ht,
                'flt_time': row.flt_time,
                'heavy': row.heavy,
                'tow_cost': row.tow_cost,
                'glider_cost': row.glider_cost,
                'billed': row.billed})

    result = True
    return result


def check_match(flights, check_id, tow_time: datetime) -> int:
    """
    Locate matching glider takeoff from Ktrax set. Following
    flight must be within "tow_time" of tug take off
    :param flights: list of flights
    :param check_id is id of tow flight to be checked against
    :param tow_time: upper time interval to determine match
    :return: the id key for the matching glider flight
    """
    found = None
    five_minutes = timedelta(seconds=300)
    found_id = None
    for line in flights:

        if line[1] >= tow_time and line[1] <= tow_time + five_minutes:
            if line[0] != check_id:
                found_id = line[0]
                break

    return (found_id)


def load_flightsheet_frame(tow) -> tuple | None:
    """Return one frame with relevant data for one tow using the tow/glider
    ident key pairs found in prior step.

    :param tow: a tuple with tow sequence number, tug ident key , glider ident key

    :return: a 'frame' namedtuple as one row of data
    """
    frame = namedtuple('frame', ['tow', 'tow_date', 'payer', 'tug_id', 'glider_id', 'tug_to',
                                 'tug_ld', 'gld_ld', 'ogn_ht', 'billed_ht', 'flt_time',
                                 'heavy', 'tow_cost', 'glider_cost', 'billed'])

    t = Web_flights.query.get(tow[1])
    g = Web_flights.query.get(tow[2])

    if g is not None:
        if g.aircraft in Folder.global_vars.club:
            g.quantity = g.flt_time
            db.session.commit()

        str_to_time = t.to_time.time().isoformat(timespec='minutes')
        if t.ld_time:
            str_tld_time = t.ld_time.time().isoformat(timespec='minutes')
        else:
            str_tld_time = ''
        if g.ld_time:
            str_gld_time = g.ld_time.time().isoformat(timespec='minutes')
        else:
            str_gld_time = ''
        this_tow_date = datetime.fromisoformat(Folder.global_vars.start_date)
        tow_cost, glider_cost = flight_cost(t, g)
        result = update_costs(t.id, tow_cost)
        result = update_bill_status(t.id, 'BILLABLE')
        result = update_costs(g.id, glider_cost)
        result = update_tow_payee(t.id, g.pilot_initials)

        data = frame(tow[0], this_tow_date, g.pilot_initials, t.aircraft, g.aircraft, str_to_time, str_tld_time,
                     str_gld_time, t.OGN_ht, t.launch_ht, g.flt_time, g.heavy, f"{tow_cost:.2f}",
                     f"{glider_cost:.2f}", 'UNBILLED')

        logging.debug(data)

        return data
    else:
        return None


def flight_cost(tug, glider) -> tuple[float, float]:
    """
    Calculate flight cost for tow and glider if club aircraft
    :param tug:  class instance of webflight
    :param glider: class instance of webflight
    :return: cost pair for tug and glider
    """
    if tug.launch_ht != 0 and tug.launch_ht is not None:
        if glider.heavy:
            tug_cost = 20 + (tug.launch_ht / 100) * 1.75
        elif not glider.heavy:
            tug_cost = 20 + (tug.launch_ht / 100) * 1.50
        else:
            tug_cost = 0.0
    else:
        tug_cost = 0.0

    if glider.aircraft in Folder.global_vars.club.keys():

        if glider.flt_time is not None and glider.pilot_initials not in Folder.global_vars.bulk_bill:
            glider_cost = glider.flt_time * Folder.global_vars.club[glider.aircraft]
        else:
            glider_cost = 0.0
    else:
        glider_cost = 0.0

    return (tug_cost, glider_cost)

