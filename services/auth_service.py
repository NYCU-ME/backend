from datetime import timezone, datetime
from enum import Enum
from email_validator import validate_email, EmailNotValidError
import jwt

class Operation(Enum):
    APPLY = 1
    RELEASE = 2
    MODIFY = 3
    RENEW = 4

class UnauthorizedError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "Unauthorized: " + self.msg

class AuthService:
    def __init__(self, logger, jwt_secret, users, domains):
        self.logger = logger
        self.jwt_secret = jwt_secret
        self.users = users
        self.domains = domains

    def issue_token(self, profile, type_):
        now = int(datetime.now(tz=timezone.utc).timestamp())
        token = profile
        token['iss'] = 'dns.nycu.me'
        token['exp'] = now + 3600
        token['iat'] = token['nbf'] = now
        token['uid'] = token['username']
        token['isAdmin'] = False
        token['type'] = type_

        user = self.users.query(token['uid'])

        if user:
            if user.email != token['email']:
                self.users.update_email(token['uid'], token['email'])
            token['isAdmin'] = user.isAdmin
        else:
            self.users.add(uid=token['uid'], name='', username='', password='',
                           status='active', email=token['email'])

        token = jwt.encode(token, self.jwt_secret, algorithm="HS256")
        return token

    def authenticate_token(self, payload):
        try:
            if not payload:
                raise UnauthorizedError("not logged")
            payload = payload.split(' ')
            if len(payload) != 2:
                raise UnauthorizedError("invalid payload")
            token_type, token = payload
            if token_type != 'Bearer':
                raise UnauthorizedError("invalid payload")
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            except Exception as e:
                self.logger.debug(str(e))
                return None
            return payload
        except UnauthorizedError as e:
            self.logger.debug(str(e))
            return None

    def authorize_action(self, uid, action, domain_name):
        if action == Operation.APPLY:
            domains = self.domains.list_by_user(uid)
            if len(domains) >= self.users.query(uid).limit:
                raise UnauthorizedError("You cannot apply for more domains.")

        domain = self.domains.get_domain(domain_name)
        if action == Operation.RELEASE:
            if domain.userId != uid:
                raise UnauthorizedError(
                        f"You cannot modify domain {domain_name} which you don't have."
                )

        if action == Operation.MODIFY:
            if domain.userId != uid:
                raise UnauthorizedError(
                        f"You cannot modify domain {domain_name} which you don't have."
                )

        if action == Operation.RENEW:
            if domain.userId != uid:
                raise UnauthorizedError(
                        f"You cannot modify domain {domain_name} which you don't have."
                )

    def verify_email(self, email):
        try:
            if not validate_email(email):
                return False
            if email.endswith('nycu.edu.tw') or email.endswith('nctu.edu.tw'):
                return False
            if email.endswith('.edu.tw'):
                return True
            return False
        except EmailNotValidError:
            return False
