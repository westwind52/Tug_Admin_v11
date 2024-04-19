import logging
import csv

from flask import render_template, request

from Folder import app
from Folder.models import Flightsheets
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


@app.route('/flight_sheet', methods=["GET", 'POST'])
def flight_sheet():
    try:
        _sheet: str = request.form.get('sheet_id')
        if _sheet is not None and _sheet.isdigit():
            chosen_sheet: int = int(_sheet)
            all_flights = Flightsheets.query.filter_by(sheet_id=chosen_sheet).all()
        else:
            chosen_sheet = 0
            all_flights = []

        if all_flights:
            logging.info(f'Flight Sheet {all_flights[0].sheet_id}')

        print_block = create_flightsheet(all_flights)
        logging.debug(print_block)
        print_pdf(print_block)

        return render_template('flightsheet.html', flt_data=all_flights, sheet=str(chosen_sheet))
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        # handle the exception or log the error
        return render_template('error.html', error=str(e))


def print_pdf(_print_block):
    doc = SimpleDocTemplate("D:\\data\\fl_sheet.pdf", pagesize=landscape(A4))
    t = Table(_print_block)
    t.setStyle(TableStyle([('BACKGROUND', (1, 1), (-2, -2), colors.green),
                           ('TEXTCOLOR', (0, 0), (1, -1), colors.red)]))
    elements = [t]
    # write the document to disk
    doc.build(elements)

    return


def create_flightsheet(_data):
    """
    id = db.Column(db.Integer, primary_key=True)
    sheet_id = db.Column(db.Integer())
    tow_date = db.Column(db.DATETIME)
    tow = db.Column(db.Integer())
    payer = db.Column(db.String())
    tug_id = db.Column(db.String())
    glider_id = db.Column(db.String())
    tug_to = db.Column(db.String())
    tug_ld = db.Column(db.String())
    gld_ld = db.Column(db.String())
    ogn_ht = db.Column(db.String())
    billed_ht = db.Column(db.Integer())
    flt_time = db.Column(db.Integer())
    heavy = db.Column(db.Boolean(), default=False)
    tow_cost = db.Column(db.Float())
    glider_cost = db.Column(db.Float())
    billed = db.Column(db.String())
    written = db.Column(db.DATETIME)
    billed_date = db.Column(db.DATETIME)
    """

    all_rows = []
    a = list(Flightsheets.__table__.columns.keys())[2:]
    all_rows.append(a)

    for row in _data:
        b = [str(row.sheet_id),
             str(row.tow),
             str(row.billed_ht),
             str(row.flt_time),
             str(row.heavy),
             row.payer,
             row.tug_id,
             row.glider_id,
             row.tug_to,
             row.tug_ld,
             row.gld_ld,
             row.ogn_ht,
             f'{row.tow_cost:.2f}',
             f'{row.glider_cost:.2f}',
             row.billed,
             f'{row.written:%Y%m%d %H:%M}',
             f'{row.billed_date:%Y%m%d %H:%M}']

        all_rows.append(b)

    items_to_print = []
    for item in all_rows:
        items_to_print.append(item[3:])

    return items_to_print


def write_flightsheets(data):
    """
    Write a 'flightsheets'  CSV file.
    Csv file written each time a data set is sent to analyse.
    :param data:
    :return:
    """

    with open('D:\\data\\sheets.csv', 'w', newline='') as csvfile:
        fieldnames = ['sheet_id', 'tow_date', 'tow', 'payer', 'tug_id', 'glider_id', 'tug_to', 'tug_ld', 'gld_ld',
                      'ogn_ht', 'billed_ht', 'flt_time', 'heavy', 'tow_cost', 'glider_cost', 'billed',
                      'written', 'billed_date']

        f = csv.DictWriter(csvfile, fieldnames=fieldnames)

        f.writeheader()
        for row in data:
            f.writerow({
                'sheet_id': row.sheet_id,
                'tow_date': row.tow_date.date().isoformat(),
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
