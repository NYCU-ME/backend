import logging
import os
from flask import Flask
import flask_cors
from sqlalchemy import create_engine

import config
from models import Users, Domains, Records, Glues, DDNS, Elastic, db
from services import AuthService, DNSService, Oauth

env_test = os.getenv('TEST')

app = Flask(__name__)
flask_cors.CORS(app)

SQL_ENGINE = None
if env_test is not None:
    SQL_ENGINE = create_engine("sqlite:///:memory:")
    db.Base.metadata.create_all(SQL_ENGINE)
else:
    connection_string = (
        f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PSWD}"
        f"@{config.MYSQL_HOST}/{config.MYSQL_DB}"
    )
    SQL_ENGINE = create_engine(connection_string)

ddns = DDNS(logging, config.DDNS_KEY, config.DDNS_SERVER, config.DDNS_ZONE)

users = Users(SQL_ENGINE)
domains = Domains(SQL_ENGINE)
records = Records(SQL_ENGINE)
glues = Glues(SQL_ENGINE)

nycu_oauth = Oauth(redirect_uri = config.NYCU_OAUTH_RURL,
                   client_id = config.NYCU_OAUTH_ID,
                   client_secret = config.NYCU_OAUTH_KEY)

elastic = Elastic(config.ELASTICSERVER, config.ELASTICUSER, config.ELASTICPASS)
authService = AuthService(logging, config.JWT_SECRET, users, domains)
dnsService = DNSService(logging, users, domains, records, glues, ddns, config.HOST_DOMAINS)

from controllers import auth, domains, ddns, glue # pylint: disable=all
