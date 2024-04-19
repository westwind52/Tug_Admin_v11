from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Web_flights(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    seq_num = db.Column(db.Integer(), unique=True)
    flt_id = db.Column(db.Integer())
    flt_class = db.Column(db.String(12))
    to_date = db.Column(db.String(12))
    to_time = db.Column(db.DATETIME())
    ld_time = db.Column(db.DATETIME())
    flt_time = db.Column(db.Integer())
    aircraft = db.Column(db.String(10))
    pilot_initials = db.Column(db.String(50))
    heavy = db.Column(db.Boolean())
    OGN_ht = db.Column(db.Integer())
    launch_ht = db.Column(db.Integer())
    bill_status = db.Column(db.String(20))
    sheet_number = db.Column(db.Integer())
    cost = db.Column(db.Float())
    pair_id = db.Column(db.Integer())
    pilot_id = db.Column(db.Integer(), db.ForeignKey('pilots.id'))

    def __init__(self, seq_num, flt_id, flt_class, to_date, to_time, ld_time, flt_time,
                 aircraft, pilot_initials, heavy, OGN_ht, launch_ht, bill_status,
                 sheet_number, cost, pair_id, pilot_id):
        self.seq_num = seq_num
        self.flt_id = flt_id
        self.flt_class = flt_class
        self.to_date = to_date
        self.to_time = to_time
        self.ld_time = ld_time
        self.flt_time = flt_time
        self.aircraft = aircraft
        self.pilot_initials = pilot_initials
        self.heavy = heavy
        self.OGN_ht = OGN_ht
        self.launch_ht = launch_ht
        self.bill_status = bill_status
        self.sheet_number = sheet_number
        self.cost = cost
        self.pair_id = pair_id
        self.pilot_id = pilot_id


class Uploads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seq_num = db.Column(db.Integer())
    category = db.Column(db.String(12))
    pilot = db.Column(db.String(50))
    invoice = db.Column(db.Integer())
    bill_date = db.Column(db.String(12))
    due_date = db.Column(db.String(12))
    item = db.Column(db.String(50))
    quantity = db.Column(db.Integer())
    price = db.Column(db.Float())
    description = db.Column(db.String())
    uploaded = db.Column(db.Boolean())

    def __init__(self, seq_num, category, pilot, invoice, bill_date,
                 due_date, item, quantity, price, description, uploaded):
        self.seq_num = seq_num
        self.category = category
        self.pilot = pilot
        self.invoice = invoice
        self.bill_date = bill_date
        self.due_date = due_date
        self.item = item
        self.quantity = quantity
        self.price = price
        self.description = description
        self.uploaded = uploaded


class Pilots(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pilot_initials = db.Column(db.String(3), unique=True)
    pilot_name = db.Column(db.String(30))
    email = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    club_member = db.Column(db.Boolean())
    contact = db.Column(db.String(50))
    flights = db.relationship('Web_flights', backref='pilot')

    def __init__(self, pilot_initials, pilot_name, email, phone, club_member, contact):
        self.pilot_initials = pilot_initials
        self.pilot_name = pilot_name
        self.email = email
        self.phone = phone
        self.club_member = club_member
        self.contact = contact


class Aircraft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration = db.Column(db.String(3), unique=True)
    make = db.Column(db.String(20))
    self_launch = db.Column(db.Boolean())
    pilot_initials = db.Column(db.String(3))
    normal_pilot = db.Column(db.String(20))
    acft_class = db.Column(db.String(10))
    heavy = db.Column(db.Boolean)

    def __init__(self, registration, make, self_launch, pilot_initials, normal_pilot, acft_class, heavy):
        """

        :type heavy: object
        """
        self.registration = registration
        self.make = make
        self.self_launch = self_launch
        self.pilot_initials = pilot_initials
        self.normal_pilot = normal_pilot
        self.acft_class = acft_class
        self.heavy = heavy


class Flightsheets(db.Model):
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

    def __init__(self, sheet_id, tow_date, tow, payer, tug_id, glider_id, tug_to,
                 tug_ld, gld_ld, ogn_ht, billed_ht, flt_time,
                 heavy, tow_cost, glider_cost, billed, written, billed_date):
        self.sheet_id = sheet_id
        self.tow_date = tow_date
        self.tow = tow
        self.payer = payer
        self.tug_id = tug_id
        self.glider_id = glider_id
        self.tug_to = tug_to
        self.tug_ld = tug_ld
        self.gld_ld = gld_ld
        self.ogn_ht = ogn_ht
        self.billed_ht = billed_ht
        self.flt_time = flt_time
        self.heavy = heavy
        self.tow_cost = tow_cost
        self.glider_cost = glider_cost
        self.billed = billed
        self.written = written
        self.billed_date = billed_date


class Ktrax(db.Model):
    __bind_key__ = 'db1'
    record_id = db.Column(db.Integer(), primary_key=True)
    seq_num = db.Column(db.Integer())
    flt_id = db.Column(db.String(10))
    fl_type = db.Column(db.Integer())
    glider = db.Column(db.String(10))
    pilot = db.Column(db.String(30))
    to_time = db.Column(db.DATETIME())
    ld_time = db.Column(db.DATETIME())
    height = db.Column(db.String(10))
    tow_ht = db.Column(db.String(10))

    def __init__(self, record_id, seq_num, flt_id, fl_type, glider,
                 pilot, to_time, ld_time, height, tow_ht):
        self.record_id = record_id
        self.seq_num = seq_num
        self.flt_id = flt_id
        self.fl_type = fl_type
        self.glider = glider
        self.pilot = pilot
        self.to_time = to_time
        self.ld_time = ld_time
        self.height = height
        self.tow_ht = tow_ht


class Sheets(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    sheet_id = db.Column(db.Integer())
    flying_day = db.Column(db.String(12))

    def __init__(self, sheet_id, flying_day):
        self.sheet_id = sheet_id
        self.flying_day = flying_day
