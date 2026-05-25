from flask import Flask
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.json.sort_keys = False #type:ignore
app.secret_key = os.getenv('secret_key', 'change-me')


from views.customers_view import *
from views.vehicle_view import *
from views.parking_record_view import *
from views.auth_user_view import *
from views.parking_spot_view import *
from views.vehicle_type_view import *
from views.auth_view import *

if __name__=='__main__':
    app.run(debug=True) #type:ignore