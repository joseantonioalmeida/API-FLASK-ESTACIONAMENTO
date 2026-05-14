from flask import Flask


app = Flask(__name__)

from views.customers_view import *
from views.vehicles_view import *
from views.parking_view import *

if __name__=='__main__':
    app.run(debug=True)