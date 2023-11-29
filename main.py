import logging
import os
import time
from flask import Flask
import flask_cors
from sqlalchemy import create_engine

import config
from models import Users, Domains, Records, Glues, DDNS, db
from services import AuthService, DNSService, Oauth

env_test = os.getenv('TEST')

app = Flask(__name__)
flask_cors.CORS(app)

sql_engine = None
if env_test is not None:
    sql_engine = create_engine("sqlite:///:memory:")
    db.Base.metadata.create_all(sql_engine)
else:
    sql_engine = create_engine(
        'mysql+pymysql://{user}:{pswd}@{host}/{db}'.format(
            user=config.MYSQL_USER,
            pswd=config.MYSQL_PSWD,
            host=config.MYSQL_HOST,
            db=config.MYSQL_DB
        )
    )

ddns = DDNS(logging, config.DDNS_KEY, config.DDNS_SERVER, config.DDNS_ZONE)

users = Users(sql_engine)
domains = Domains(sql_engine)
records = Records(sql_engine)
glues = Glues(sql_engine)

nycu_oauth = Oauth(redirect_uri = config.NYCU_OAUTH_RURL,
                   client_id = config.NYCU_OAUTH_ID,
                   client_secret = config.NYCU_OAUTH_KEY)

authService = AuthService(logging, config.JWT_SECRET, users, domains)
dnsService = DNSService(logging, users, domains, records, glues, ddns, config.HOST_DOMAINS)

@app.route("/")
def index():
    return "Hello World!"

from controllers import auth, domains, ddns, glue
