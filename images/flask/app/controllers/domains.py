from flask import g
from main import app, authService, dnsService
from services import Operation

@app.route("/domains", methods=['GET'])
def list_domains():
    if not g.user:
        return {"msg": "Unauth."}, 401
    if not g.user['isAdmin']:
        return {"msg": "Unauth."}, 403

    return {"msg": "ok", "data": dnsService.list_domains()}

@app.route("/domains/<path:domain>", methods=['POST'])
def register_domain(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.replace('.', '/').lower().strip('/').split('/')
    domain_name = '.'.join(reversed(domain_struct))

    if not g.user['isAdmin'] and len(domain_struct[-1]) < 4:
        return {"msg": "Length must be greater than 3."}, 400

    if dnsService.check_domain(domain_name) != len(domain_struct):
        return {"msg": "Not valid domain name."}, 400

    try:
        if not g.user['isAdmin']:
            authService.authorize_action(g.user['uid'], Operation.APPLY, domain_name)
        dnsService.register_domain(g.user['uid'], domain_name)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": str(e)}, 403

@app.route("/domains/<path:domain>", methods=['DELETE'])
def release_domain(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name = '.'.join(reversed(domain_struct))

    try:
        if not g.user['isAdmin']:
            authService.authorize_action(g.user['uid'], Operation.RELEASE, domain_name)
        dnsService.release_domain(domain_name)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": str(e)}, 403

@app.route("/renew/<path:domain>", methods=['POST'])
def renew_domain(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name = '.'.join(reversed(domain_struct))

    try:
        if not g.user['isAdmin']:
            authService.authorize_action(g.user['uid'], Operation.RENEW, domain_name)
        dnsService.renew_domain(domain_name)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": str(e)}, 403

@app.route("/domain/<string:domain_id>", methods=['GET'])
def get_domain_by_id(domain_id):

    if not domain_id.isnumeric():
        return {"msg": "Invalid id."}, 400

    if not g.user:
        return {"msg": "Unauth."}, 401

    domain = dnsService.get_domain_by_id(int(domain_id))
    if domain is None:
        return {"msg": "No such entry."}, 404
    try:
        if not g.user['isAdmin']:
            authService.authorize_action(g.user['uid'], Operation.MODIFY, domain['domain'])
        return {"msg": "ok", "domain": domain}
    except Exception as e:
        return {"msg": str(e)}, 403
