from __future__ import with_statement
from flask import Flask
from dashboard.utils import *
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import timedelta
from config import *
from utils import *

# configuration
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)

app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['PROPAGATE_EXCEPTIONS'] = True

db_conn = DB_URL
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn
db = SQLAlchemy(app)

app.permanent_session_lifetime = timedelta(minutes=60*3)

from dashboard.products import ComponentsTracker


def init_db():
    """Creates the database tables."""
    #db.drop_all()
    db.create_all()
    ct = ComponentsTracker()


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""


app.jinja_env.globals.update(getTrackedBugs=getTrackedBugs)
app.jinja_env.globals.update(getUserQueryBugs=getUserQueryBugs)
app.jinja_env.globals.update(getAssignedBugs=getAssignedBugs)
app.jinja_env.globals.update(getUnassignedBugs=getUnassignedBugs)
app.jinja_env.globals.update(getProdCompBugs=getProdCompBugs)
app.jinja_env.globals.update(getNeedsInfoBugs=getNeedsInfoBugs)
app.jinja_env.globals.update(getToFollowBugs=getToFollowBugs)
app.jinja_env.globals.update(getToNominateBugs=getToNominateBugs)
app.jinja_env.globals.update(getToApproveBugs=getToApproveBugs)
app.jinja_env.globals.update(getToUpliftBugs=getToUpliftBugs)
app.jinja_env.globals.update(getKeywords=getKeywords)
app.jinja_env.globals.update(getComponents=getComponents)

if __name__ == '__main__':
    #init_db()
    app.run()

from relmandash.models import *
import views_account
