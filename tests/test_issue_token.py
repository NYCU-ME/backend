from sqlalchemy import create_engine
import logging

from services.authService import AuthService
from models import users
from config import *

sql_engine = create_engine(
    'mysql+pymysql://{user}:{pswd}@{host}/{db}'.format(
        user=MySQL_User,
        pswd=MySQL_Pswd,
        host=MySQL_Host,
        db=MySQL_DB
    )
)
users = users.Users(sql_engine)
authService = AuthService(logging, JWT_secretKey, users)

testdata = [{"email":"lin.cs09@nycu.edu.tw","username":"109550028"}]

def test_issue_token():
	for testcase in testdata:
		token = "Bearer " + authService.issue_token(testcase)
		assert authService.authenticate_token(token)
		assert authService.authenticate_token(token + 'a')  == None # modified token

