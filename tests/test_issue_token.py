import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.auth_service import AuthService
from models import Users, Domains, db
import config

sql_engine = create_engine('sqlite:///:memory:')
db.Base.metadata.create_all(sql_engine)
Session = sessionmaker(bind=sql_engine)
session = Session()

users = Users(sql_engine)
domains = Domains(sql_engine)
authService = AuthService(logging, config.JWT_SECRET, users, domains)

testdata = [{'email':"lin.cs09@nycu.edu.tw",'username':"109550028"},
            {'email':"lin.cs09@nctu.edu.tw",'username':"109550028"}]

def test_issue_token():
    for testcase in testdata:
        token = "Bearer " + authService.issue_token(testcase)
        assert authService.authenticate_token(token) is not None
        # test modified token
        assert authService.authenticate_token(token + 'a') is None
        # test if data is written
        session.expire_all()# flush orm cache
        data = session.query(db.User).filter_by(id=testcase['username']).all()
        assert len(data) and data[0].email == testcase['email']
