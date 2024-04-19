from decimal import Decimal
from dataclasses import dataclass
import dateutil.relativedelta
from datetime import datetime, date, time, timedelta
from collections import namedtuple
import csv
from sqlalchemy import and_
from flask import render_template
from Folder import app
from Folder.models import Uploads, Flightsheets
import Folder.global_vars


@app.route('/upload')
def upload():
    """
    This function handles the upload route.
    """
    print("IN Upload---")
    get_date = Folder.global_vars.start_date
    dt_start_date = date.fromisoformat(get_date)
    dt_end_date = dt_start_date + dateutil.relativedelta.relativedelta(days=30)

    # db.session.query(Uploads).delete()
    # db.session.commit()
    data_frame = []
    all_uploads = Flightsheets.query.filter(Flightsheets.tow_date.between(dt_start_date, dt_end_date)).all()

    for row in all_uploads:
        rec = make_billing_data_fs(row, 'TUG')
        data_frame.append(rec)

    result = write_upload(data_frame)

    return render_template("upload.html", flt_data=data_frame)



# @app.route('/billing data')
# def billing_data():
#     """Import Webflights  data from a stored Webflights  database table
#      and store in different format in Upload database table
#      :return: Data transferred to a Upload database
#      """
#     get_date = Folder.global_vars.start_date
#     dt_get_date = date.fromisoformat(get_date)
#
#     # db.session.query(Uploads).delete()
#     # db.session.commit()
#
#     all_uploads = Web_flights.query.filter(Web_flights.to_date == dt_get_date).order_by(Web_flights.flt_id).all()
#
#     for row in all_uploads:
#         if row.aircraft in Folder.global_vars.tugs or \
#                 (row.aircraft in Folder.global_vars.club and \
#                  row.pilot_initials in Folder.global_vars.bulk_bill):
#
#             duplicate_upload = check_duplicate_uploads(row.id)
#             if not duplicate_upload:
#                 seq_num = row.id
#
#                 #my_upload = Uploads(row.seq_num, row.flt_class, row.pilot_initials, invoice, row.to_date, row.to_date,
#                 #                    row.flt_class, 1, 0.0,
#                 #                    my_idstr, billing)
#                 print(upload)
#                 # db.session.add(my_upload)
#                 # db.session.commit()
#                 # print(f"upload added {row.to_time}")
#             else:
#                 # print(f"Upload already present {row.to_time}")
#                 pass
#
#     return redirect(url_for('upload'))
#

# === Utilities ======

@dataclass
class Record:
    seq_num: int
    flt_class: str
    pilot_initials: str
    invoice: int
    bill_date: datetime.date
    due_date: datetime.date
    item: str
    quantity: int
    price: Decimal
    description: str
    billing: str
    to_time_stamp: datetime

def generate_invoice_number():
    Folder.global_vars.last_invoice += 1
    return Folder.global_vars.last_invoice

def generate_idstr(row):
    return f'{row.tow_date} {str(row.launch_ht)}ft'

def make_billing_data_tow(row):
    seq_num=row.id
    invoice = generate_invoice_number()
    bill_date = row.to_date
    item = "TUG"
    quantity = 1
    billing = 'NOTSENT'
    my_idstr = generate_idstr(row)

    rec = Record(seq_num, row.flt_class, row.pilot_initials, invoice, bill_date, bill_date,
                 item, quantity, Decimal(row.cost).quantize(Decimal('0.00')), my_idstr, billing, row.to_time)

    return rec

class Record1:
    def __init__(self, seq_num, flt_class, pilot_initials, invoice, bill_date, due_date,
                 item, quantity, price, description, billing, to_time_stamp):
        self.seq_num = seq_num
        self.flt_class = flt_class
        self.pilot_initials = pilot_initials
        self.invoice = invoice
        self.bill_date = bill_date
        self.due_date = due_date
        self.item = item
        self.quantity = quantity
        self.price = price
        self.description = description
        self.billing = billing
        self.to_time_stamp = to_time_stamp

def make_billing_data_fs(row, flt_type):
    seq_num=row.id
    invoice = Folder.global_vars.last_invoice + 1
    Folder.global_vars.last_invoice += 1
    bill_date = row.tow_date.strftime("%Y-%m-%d")

    t = time.fromisoformat(row.tug_to)
    to_time_stamp = datetime.combine(row.tow_date, t)

    handlers = {
        'TUG': handle_tug,
        'UIU': handle_uiu,
        'GLH': handle_glh
    }

    def handle_tug(row):
        item = "TUG"
        quantity = 1
        billing = 'NOTSENT'
        my_idstr = f'{row.glider_id} {bill_date} {str(row.billed_ht)}ft'

        return Record1(seq_num, flt_type, row.payer, invoice, bill_date, bill_date,
                      item, quantity, Decimal(row.tow_cost).quantize(Decimal('0.00')), my_idstr, billing, to_time_stamp)

    def handle_uiu(row):
        if row.glider_cost > 0:
            item = row.glider_id
            quantity = 1
            billing = 'NOTSENT'
            my_idstr = f'{row.glider_id} {bill_date} {str(row.flt_time)} mins'

            return Record(seq_num, flt_type, row.payer, invoice, bill_date, bill_date,
                          item, quantity, Decimal(row.glider_cost).quantize(Decimal('0.00')), my_idstr, billing, to_time_stamp)

    def handle_glh(row):
        if row.glider_cost > 0:
            item = row.glider_id
            quantity = 1
            billing = 'NOTSENT'
            my_idstr = f'{row.glider_id} {bill_date} {str(row.flt_time)} mins'

            return Record1(seq_num, flt_type, row.payer, invoice, bill_date, bill_date,
                          item, quantity, Decimal(row.glider_cost).quantize(Decimal('0.00')), my_idstr, billing, to_time_stamp)

    rec = handlers.get(flt_type, lambda row: None)(row)
    return rec

def check_duplicate_uploads(id):
    """Check for pre existing record in the Uploads table to prevent inserting a duplicate record

    :param  id this is the "seq_num" data element to be checked
    :return:  Bool true / False to indicate duplicate
    """
    my_count = Uploads.query.filter_by(seq_num=id).count()
    if my_count > 0:
        result = True
    else:
        result = False

    print("Check duplicate", result)
    return result

def write_upload(data):
    """
    Write a 'upload sheet'  CSV file.

    :param data:
    :return:
    """

    with open('D:\DATA\\upload.csv', 'a', newline='') as csvfile:
        fieldnames = ['seq_num', 'flt_class', 'pilot_initials', 'invoice', 'bill_date', 'due_date',
                                       'item', 'quantity', 'price', 'description', 'billing', 'to_time_stamp']


        f = csv.DictWriter(csvfile, fieldnames=fieldnames)

        f.writeheader()
        for row in data:
            f.writerow({
                'seq_num':  row.seq_num,
                'flt_class': row.flt_class,
                'pilot_initials':  row.pilot_initials,
                'invoice':  row.invoice,
                'bill_date':  row.bill_date,
                'due_date':  row.due_date,
                'item':  row.item,
                'quantity':  row.quantity,
                'price':  row.price,
                'description':  row.description,
                'billing':  row.billing,
                'to_time_stamp': row.to_time_stamp})


    result = True
    return result
