from flask import Flask

from flask_bootstrap import Bootstrap
from Folder.models import db
from Folder.config import Config
import Folder.global_vars

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
Bootstrap(app)

from Folder import models
from Folder.models import Aircraft, Pilots, Sheets
from Folder.myroutes import webflights, uploads, index, pilots, aircraft, analyse, flightsheets

@app.before_first_request
def create_table():
    db.create_all()
    return

@app.before_first_request
def load_audit_tables():
    acft = Aircraft.query.all()
    for ac in acft:
        Folder.global_vars.known_aircraft.add(ac.registration)
    print(f" Aircraft: { Folder.global_vars.known_aircraft}")

    all_pilots = Pilots.query.all()
    for p in all_pilots:
        Folder.global_vars.known_pilots.add(p.pilot_initials)

    print(f" Pilots: {Folder.global_vars.known_pilots}")
    return


if __name__ == '__main__':
    app.run(debug=True)
