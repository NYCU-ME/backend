from sqlalchemy.orm import sessionmaker
from datetime import timezone, datetime
from models import db
import jwt

class AuthService:
    def __init__(self, logger, jwt_secret, sql_engine):
        self.logger = logger
        self.jwt_secret = jwt_secret
        self.sql_engine = sql_engine

    def issue_token(self, profile):
        now = int(datetime.now(tz=timezone.utc).timestamp())
        token = profile
        token['iss'] = 'dns.nycu.me'
        token['exp'] = (now) + 3600
        token['iat'] = token['nbf'] = now
        token['uid'] = token['username']
        
        Session = sessionmaker(bind=self.sql_engine)
        session = Session()
        user = session.query(db.User).filter_by(id=token['uid']).all()

        if len(user):
            user = user[0]
            if user.email != token['email']:
                user.email = token['email']
                session.commit()
        else:
            user = db.User(id=token['uid'], name='', username='', password='', status='active', email=token['email'])
            session.add(user)
            session.commit()
        token = jwt.encode(token, self.jwt_secret, algorithm="HS256")
        return token
