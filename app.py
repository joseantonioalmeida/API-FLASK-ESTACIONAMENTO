from flask import Flask


app = Flask(__name__)
app.json.sort_keys = False #type:ignore


from views.customers_view import *
from views.vehicles_view import *
from views.parking_record_view import *
from views.auth_user_view import *
from views.parking_spot_view import *
from views.vehicle_type_view import *

if __name__=='__main__':
    app.run(debug=True) #type:ignore