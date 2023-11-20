from sqlalchemy.orm import sessionmaker
from datetime import timezone, datetime
import jwt

class UnauthorizedError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "Unauthorized: " + self.msg

class AuthService:
    def __init__(self, logger, jwt_secret, users):
        self.logger = logger
        self.jwt_secret = jwt_secret
        self.users = users

    def issue_token(self, profile):
        now = int(datetime.now(tz=timezone.utc).timestamp())
        token = profile
        token['iss'] = 'dns.nycu.me'
        token['exp'] = (now) + 3600
        token['iat'] = token['nbf'] = now
        token['uid'] = token['username']
        
        user = self.users.query(token['uid'])

        if user:
            if user.email != token['email']:
                self.users.update(token['uid'], token['email'])
        else:
            self.users.add(uid=token['uid'], name='', username='', password='', status='active', email=token['email'])

        token = jwt.encode(token, self.jwt_secret, algorithm="HS256")
        return token
    
    def authenticate_token(self, payload):
        try:
            if not payload:
                raise UnauthorizedError("not logged")
            payload = payload.split(' ')
            if len(payload) != 2:
                raise UnauthorizedError("invalid payload")
            tokenType, token = payload
            if tokenType != 'Bearer': 
                raise UnauthorizedError("invalid payload")
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            except Exception as e:
                self.logger.debug(e.__str__())
                return None
            return payload
        except UnauthorizedError as e:
            self.logger.debug(e.__str__())
            return None

