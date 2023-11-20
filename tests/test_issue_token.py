from unittest.mock import create_autospec
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.base import Engine
import logging

from services.authService import AuthService
from models import users, db
from config import *

sql_engine = create_engine('sqlite:///:memory:') 
db.Base.metadata.create_all(sql_engine)
Session = sessionmaker(bind=sql_engine)
session = Session()

users = users.Users(sql_engine)
authService = AuthService(logging, JWT_secretKey, users)

testdata = [{'email':"lin.cs09@nycu.edu.tw",'username':"109550028"}]

def test_issue_token():
	for testcase in testdata:
		token = "Bearer " + authService.issue_token(testcase)
		assert authService.authenticate_token(token) != None
        # test modified token
		assert authService.authenticate_token(token + 'a')  == None 
        # test if data is written
		assert len(session.query(db.User).filter_by(id=testcase['username']).all()) 
