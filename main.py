from flask import Flask, g, Response, request, abort
import flask_cors
import logging
from sqlalchemy import create_engine

from config import *
from models import users
from services import *

app = Flask(__name__)
flask_cors.CORS(app)

sql_engine = create_engine(
    'mysql+pymysql://{user}:{pswd}@{host}/{db}'.format(
        user=MySQL_User,
        pswd=MySQL_Pswd,
        host=MySQL_Host,
        db=MySQL_DB
    )
)

users = users.Users(sql_engine)
nycu_oauth = Oauth(redirect_uri = NYCU_Oauth_rURL,
                   client_id = NYCU_Oauth_ID,
                   client_secret = NYCU_Oauth_key)

authService = AuthService(logging, JWT_secretKey, users)

@app.route('/')
def hello_world():
    return 'Hello, World.'

from controllers import *
