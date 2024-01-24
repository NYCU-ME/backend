from flask import request, g

from main import app, authService, dnsService
from services import Operation

@app.route("/dnssec/<path:domain>/records/", methods=['POST'])
def add_dnssec_record(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name = '.'.join(reversed(domain_struct))

    try:
        req = request.json
        flag = int(req.get('flag'))
        algorithm = int(req.get('algorithm'))
        value = req.get('value', "")
        ttl = int(req.get('ttl', 5))

        if flag != 256 or flag != 257:
            raise ValueError("Invalid flag value.")
        
        if not 5 <= ttl <= 86400:
            raise ValueError("TTL must be between 5 and 86400.")

        if value.count('\n'):
            raise ValueError("Invalid value format.")

    except ValueError as e:
        return {"msg": f"Invalid input: {e}"}, 400

    try:
        if not g.user.get('isAdmin', False):
            authService.authorize_action(g.user['uid'], Operation.MODIFY, domain_name)
        dnsService.add_dnssec_key(domain_name, flag, algorithm, value, ttl)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": str(e)}, 403

@app.route("/dnssec/<path:domain>/records/", methods=['DELETE'])
def del_dnssec_record(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name   = '.'.join(reversed(domain_struct))

    try:
        req = request.json
        flag = int(req.get('flag'))
        if flag != 256 or flag != 257:
            raise ValueError("Invalid flag value.")
        algorithm = int(req.get('algorithm'))
        value = req.get('value', "")

        if value.count('\n'):
            raise ValueError("Invalid value format.")

    except ValueError as e:
        return {"msg": f"Invalid input: {e}"}, 400

    try:
        if not g.user['isAdmin']:
            authService.authorize_action(g.user['uid'], Operation.MODIFY, domain_name)
        dnsService.del_dnssec_key(domain_name, flag, algorithm, value)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": str(e)}, 403
