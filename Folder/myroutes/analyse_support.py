import traceback
from dataclasses import dataclass
from collections import namedtuple
import csv
import logging
from datetime import timedelta
from typing import Any, Optional

import Folder.global_vars
from Folder.models import Flightsheets
from Folder.myroutes.my_utils import *


def find_tows(_flights: Web_flights, self_launch: list, tugs: list) -> (list[int, int, int], list):
    """
    Find the towplane-glider pairs from a list of flights.

    Args:
        _flights (list): List of flights.
        self_launch (list): List of self-launch aircraft.
        tugs (list): List of towplane aircraft.

    Returns:
        tuple: A tuple containing towplane-glider pairs and unknown towplanes.
    """
    my_tows: list[int, int, int] = []
    my_data = [(row.id, row.to_time, row.aircraft, row.flt_class) for row in _flights]
    unknown_tows = []

    tow_count = 1
    glider_ids = {}
    for line in my_data:
        if line[2] in self_launch:
            continue
        elif line[2] in tugs:
            _tow_id = line[0]
            if _glider_id := glider_ids.get(_tow_id):
                my_tows.append((tow_count, _tow_id, _glider_id))
                tow_count += 1
            else:
                assert isinstance(_tow_id)
                unknown_tows.append(_tow_id)
            glider_ids[_tow_id] = _glider_id

    return my_tows, unknown_tows


def find_glider_id(_my_data, _line, _my_tows: list, _unknown_tows: list, _tow_count: int) -> tuple[list, list, int]:
    """

    :param _my_data: 
    :param _line: 
    :param _my_tows: list
    :param _unknown_tows: list
    :return: list, list, int
    :type _tow_count: object
    """
    _tow_id = _line[0]
    if _glider_id := check_match(_my_data, _tow_id, _line[1]):
        _my_tows.append((_tow_count, _tow_id, _glider_id))
        _tow_count += 1
    else:
        assert isinstance(_tow_id)
        _unknown_tows.append(_tow_id)
    return _my_tows, _unknown_tows, _tow_count


def build_tow_pairs(flight_data: list[Web_flights]) -> (list, list, list):
    """

    :param flight_data: 
    :return: 
    """
    unknown_tow: list[int] = []
    no_height: list[int] = []

    # generate the found tows list and remaining unknowns
    found_tows, unknown_tows = find_tows(flight_data)
    # -- Assemble the data from of the two paired tow plane and glider flights using the list from above

    data_frame: list[Frame | None] = [load_flightsheet_frame(tow) for tow in found_tows if
                                      load_flightsheet_frame(tow).billed_ht == 0]
    no_height = [tow[1] for tow in found_tows if load_flightsheet_frame(tow).billed_ht == 0]

    return data_frame, no_height, unknown_tow


def transfer_flightsheet(file_path: str):
    """
    Transfer contents of a stored CSV one day flightsheet file to db table flight sheets
    :param file_path: The path of the CSV file to transfer
    :return:
    """
    try:
        with open(file_path, newline='') as csvfile:
            f = csv.DictReader(csvfile)
            rows = []
            for row in f:
                row['heavy'] = row['heavy'] == 'True'
                dt_tow_date = datetime.fromisoformat(row['tow_date'])
                row['tow_date'] = dt_tow_date
                dt_written = datetime.fromisoformat(row['written'])
                row['written'] = dt_written
                dt_billed_date = datetime.fromisoformat(row['billed_date'])
                row['billed_date'] = dt_billed_date

                data = Flightsheets(**row)
                rows.append(data)

            db.session.add_all(rows)
            db.session.commit()
    except Exception as e:
        logging.error(f"An error occurred during database operations: {str(e)}")


def load_flightsheets(data: object) -> bool:
    """
    Write a 'flightsheets'  CSV file.
    Csv file written each time a data set is sent to analyse.
    :param data:
    :return: resutl bool
    """

    with open('D:\\data\\sheets1.csv', 'w', newline='') as csvfile:
        fieldnames = ['sheet_id', 'tow_date', 'tow', 'payer', 'tug_id', 'glider_id', 'tug_to', 'tug_ld', 'gld_ld',
                      'ogn_ht', 'billed_ht', 'flt_time', 'heavy', 'tow_cost', 'glider_cost', 'billed',
                      'written', 'billed_date']

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
                'billed': row.billed,
                'written': row.written,
                'billed_date': row.billed_date})
    return True


def check_match(flights, check_id: int, tow_time: datetime) -> int | None:
    """
    Locate matching glider takeoff from Ktrax set. Following
    flight must be within "tow_time" of tug take off
    :param flights: list of flights
    :param check_id is id of tow flight to be checked against
    :param tow_time: upper time interval to determine match
    :return: the id key for the matching glider flight
    """
    five_minutes = timedelta(seconds=300)

    for line in flights:
        found_id = None
        if tow_time <= line[1] <= tow_time + five_minutes:
            if line[0] != check_id:
                found_id = line[0]
                return found_id

    return None


@dataclass
class Frame:
    tow: Any
    tow_date: Any
    payer: Any
    tug_id: Any
    glider_id: Any
    tug_to: Any
    tug_ld: Any
    gld_ld: Any
    ogn_ht: Any
    billed_ht: Any
    flt_time: Any
    heavy: Any
    tow_cost: Any
    glider_cost: Any
    billed: Any
    written: Any
    billed_date: Any


def load_flightsheet_frame(tow) -> Optional[Frame]:
    """Return one frame with relevant data for one tow using the tow/glider
    ident key pairs found in prior step.

    :param tow: a tuple with tow sequence number, tug identity key , glider identity key

    :return: a 'frame' object as one row of data
    """
    t = Web_flights.query.get(tow[1])
    g = Web_flights.query.get(tow[2])

    if g is not None:
        return extract_data_for_load_flightsheet_frame(g, t,  tow)
    else:
        return None



def Web_flights_query_get(ids):
    # implementation of Web_flights.query.get function
    pass


def Web_flights_query_filter(ids):
    # implementation of Web_flights.query.filter function
    pass


def extract_data_for_load_flightsheet_frame(g: Web_flights, t: Web_flights, tow: tuple) -> Frame | None:
    try:
        if g.aircraft in Folder.global_vars.club:  # check if its a club glider
            g.quantity = g.flt_time  # if so set the number of minutes
            db.session.flush()

        str_to_time = t.to_time.time().isoformat(timespec='minutes')
        str_tld_time = (
            t.ld_time.time().isoformat(timespec='minutes') if t.ld_time else ''
        )
        if g.ld_time:
            str_gld_time = g.ld_time.time().isoformat(timespec='minutes')
        else:
            str_gld_time = ''
        this_tow_date = datetime.fromisoformat(Folder.global_vars.start_date)

        try:
            tow_cost, glider_cost = flight_cost(t, g)
        except Exception as e:
            print(f"Error calculating flight cost: {e}")
            tow_cost = 0.0
            glider_cost = 0.0

        result = update_costs(t.id, tow_cost)
        if result is None:
            print("Error updating tow cost")
        result = update_bill_status(t.id, 'BILLABLE')
        if result is None:
            print("Error updating bill status for tow")
        result = update_costs(g.id, glider_cost)
        if result is None:
            print("Error updating glider cost")
        if glider_cost > 0.0:
            result = update_bill_status(g.id, 'BILLABLE')
            if result is None:
                print("Error updating bill status for glider")
        else:
            result = update_bill_status(g.id, 'NO BILL')
            if result is None:
                print("Error updating bill status for glider")
        result = update_tow_payee(t.id, g.pilot_initials)
        if result is None:
            print("Error updating tow payee")

        written = datetime.utcnow()
        billed_date = written

        if g.pilot_initials is not None and g.pilot_initials != '':
            payer = g.pilot_initials
        else:
            payer = None

        result = Frame(
            tow=tow[0],
            tow_date=this_tow_date,
            payer=payer,
            tug_id=t.aircraft,
            glider_id=g.aircraft,
            tug_to=str_to_time,
            tug_ld=str_tld_time,
            gld_ld=str_gld_time,
            ogn_ht=t.OGN_ht,
            billed_ht=t.launch_ht,
            flt_time=g.flt_time,
            heavy=g.heavy,
            tow_cost=f"{tow_cost:.2f}",
            glider_cost=f"{glider_cost:.2f}",
            billed='UNBILLED',
            written=written,
            billed_date=billed_date,
        )

        return result
    except Exception as e:
        traceback.print_exc()
        return None


TUG_BASE_COST = 20
TUG_COST_PER_LAUNCH_HT_HEAVY = 1.75
TUG_COST_PER_LAUNCH_HT_NORMAL = 1.50


def flight_cost(tug, glider) -> dict[str, float]:
    """
    Calculate flight cost for tow and glider if club aircraft
    :param tug:  class instance of webflight
    :param glider: class instance of webflight
    :return: dictionary with cost for tug and glider
    """
    tug_cost: float
    glider_cost: float

    if tug.launch_ht is None:
        tug_cost = 0.0
    elif glider.heavy:
        tug_cost = TUG_BASE_COST + (tug.launch_ht / 100) * TUG_COST_PER_LAUNCH_HT_HEAVY
    else:
        tug_cost = TUG_BASE_COST + (tug.launch_ht / 100) * TUG_COST_PER_LAUNCH_HT_NORMAL

    if glider.is_club_aircraft():
        if glider.has_flight_time() and not glider.is_bulk_billed():
            glider_cost = glider.flt_time * glider.get_cost_per_minute()
        else:
            glider_cost = 0.0
    else:
        glider_cost = 0.0

    return {'tug_cost': tug_cost, 'glider_cost': glider_cost}


def update_costs(ident: int, cost: float) -> object:
    """
    :param ident: int
    :param cost: float
    :return: 
    """
    try:
        rec = Web_flights.query.get(ident)
        if rec:
            rec.cost = cost
            db.session.commit()
            return "Cost updated successfully"
        else:
            return "Record does not exist"
    except Exception as e:
        print(f"Error updating costs: {e}")
        return False


def update_tow_payee(ident: int, payee: str) -> bool:
    """

    :param ident: int
    :param payee: str
    :return: bool
    """
    try:
        rec = Web_flights.query.get(ident)
        if rec is None:
            return False
        rec.pilot_initials = payee
        db.session.flush()
    except Exception as e:
        print(f'Error updating tow payee: {e}')
        return False

    return True


def update_bill_status(ident: int, token: str) -> bool:
    """
    update the bill status with the assigned token value
    :param ident: record identifier
    :param token: the string value to be assigned
    :return: False if the operation fails
    """
    try:
        rec = Web_flights.query.filter_by(id=ident).first()
        if rec is not None:
            if token not in ['BILLABLE', 'NO BILL']:
                raise ValueError("Invalid bill status token")
            rec.bill_status = token
            db.session.flush()
        else:
            return False
    except Exception as e:
        print(f'Error updating bill status: {e}')
        return False

    return True
