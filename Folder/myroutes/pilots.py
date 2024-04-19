from csv import DictReader

from flask import render_template, request, redirect, url_for, flash
from Folder import app, db
from Folder.models import Pilots

@app.route('/pilots')
def pilot_index():
    all_data = Pilots.query.all()

    return render_template('pilots.html', pilots_data=all_data)


@app.route('/pilots/insert', methods=['POST'])
def pilot_insert():
    if request.method != 'POST':
        return
    pilot_initials = request.form['pilot_initials']
    pilot_name = request.form['pilot_name']
    email = request.form['email']
    phone = request.form['phone']
    ret = request.form['club_member']
    club_member = ret == "Y"
    contact = ''
    print(pilot_initials, pilot_name,  email, phone, club_member, contact)

    my_data = Pilots(pilot_initials, pilot_name,  email, phone, club_member, contact)
    db.session.add(my_data)
    db.session.commit()
    flash('Pilot inserted ')
    return redirect(url_for('pilot_index'))


@app.route('/pilot/update', methods=['GET', 'POST'])
def pilot_update():
    if request.method != 'POST':
        return
    my_data = Pilots.query.get(request.form.get('id'))
    my_data.pilot_initials = request.form['pilot_initials']
    my_data.pilot_name = request.form['pilot_name']
    my_data.email = request.form['email']
    my_data.phone = request.form['phone']
    ret = request.form['club_member']
    my_data.club_member = ret == "True"
    my_data.contact = request.form['contact']
    record = get_pilot_object(my_data.pilot_initials)

    db.session.commit()

    flash("Pilot Updated Successfully")

    return redirect(url_for('pilot_index'))


@app.route('/pilot/delete/<id>/', methods=['GET', 'POST'])
def pilot_delete(_id):
    my_data = Pilots.query.get(_id)
    db.session.delete(my_data)
    db.session.commit()
    flash('Employee deleted')

    return redirect(url_for('pilot_index'))


@app.route('/pilots/get_csv')
def pilot_get_csv():

    with open('d:/DATA/pilots.csv', newline='') as csvfile:
        ...
        all_pilots = DictReader(csvfile)
        print("opened file")

        for row in all_pilots:

            pilot = Pilots.query.filter(Pilots.pilot_initials == row['initials']).all()
            if len(pilot) >= 0:
                print(" No existing pilot")
                row['club_member'] = row['club_member'] == 'TRUE'
                my_data = Pilots(row['initials'], row['pilot_name'], row['email'],
                                    row['phone'], row['club_member'],row['contact'])

                print(f"Mydata: {my_data}")
                db.session.add(my_data)
                db.session.commit()
            else:
                print('Existing pilot')

    return redirect(url_for('pilot_index'))

def get_pilot_object(initials: str):

    rec = Pilots.query.filter_by(pilot_initials=initials).first()
    if rec is not None:
        print(f"PILOT Found:{rec.pilot_initials}")
    else:
        print(f"Pilot not found  {initials}")

    return rec
