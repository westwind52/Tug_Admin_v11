from collections import namedtuple
from sqlalchemy import and_
from flask import render_template, request, redirect, url_for, flash
from Folder import app, db
from Folder.models import Web_flights, Uploads
import Folder.global_vars

@app.route('/process')
def upload():
    """Transfer Webflights data to Upload formatted table

    :return: Data base table -- Upload
    """



    return render_template('process.html', up_data=updata)


@app.route('/process_insert', methods=['GET', 'POST'])
def process_insert():
    """Insert new table entry for the Upload format ( rarely used)
    uses modal screen on Upload page
    :return: New database table record
    """
    if request.method == 'POST':

        pilot = request.form['pilot']
        invoice = request.form['invoice']
        bill_date = request.form['bill_date']
        due_date = request.form['due_date']
        item = request.form['item']
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description']
        #row_active = request.form['row_active']

        my_upload = Uploads(pilot, invoice, bill_date, due_date, item, quantity, price, description)
        db.session.add(my_upload)
        db.session.commit()

        flash("upload Inserted Successfully")

    return redirect(url_for('upload'))


@app.route('/process_update', methods=['GET', 'POST'])
def process_update():
    """ Edit data on a single Upload record

    :return: Edited record stored in database
    """
    if request.method == 'POST':
        print("ID: ", request.form.get('id'))
        my_data = Processed.query.get(1)
        my_data.pilot = request.form['pilot']
        my_data.invoice = request.form['invoice']
        my_data.bill_date = request.form['bill_date']
        my_data.due_date = request.form['due_date']
        my_data.quantity = request.form['quantity']
        my_data.price = request.form['price']
        my_data.description = request.form['description']

        db.session.commit()

        flash("Processed flight Update Successfully")

    return redirect(url_for('Process'))

