from flask import Flask
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.json.sort_keys = False #type:ignore


from views.customers_view import *
from views.vehicle_view import *
from views.parking_record_view import *
from views.auth_user_view import *
from views.parking_spot_view import *
from views.vehicle_type_view import *
from views.auth_view import *
from jwt_utils import token_requerido  # JWT utilities (usado pelo decorator @token_requerido)

if __name__=='__main__':
    app.run(debug=True) #type:ignore