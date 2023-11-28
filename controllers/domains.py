from flask import Response, request, g
from main import app, authService, dnsService
from services import Operation

import logging

@app.route("/domains/<path:domain>", methods=['POST'])
def register_domain(domain):

    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.replace('.', '/').lower().strip('/').split('/')
    domain_name   = '.'.join(reversed(domain_struct))

    if len(domain_struct[-1]) < 4:
        return {"msg": "Length must be greater than 3."}, 400

    if dnsService.check_domain(domain_name) != len(domain_struct):
        return {"msg": "You can only register specific level domain name."}, 400

    try:
        authService.authorize_action(g.user['uid'], Operation.APPLY, domain_name)
        dnsService.register_domain(g.user['uid'], domain_name)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": e.msg}, 403

@app.route("/domains/<path:domain>", methods=['DELETE'])
def release_domain(domain):

    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name   = '.'.join(reversed(domain_struct))

    try:
        authService.authorize_action(g.user['uid'], Operation.RELEASE, domain_name)
        dnsService.release_domain(domain_name)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": e.msg}, 403

@app.route("/renew/<path:domain>", methods=['POST'])
def renew_domain(domain):

    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name   = '.'.join(reversed(domain_struct))

    try:
        authService.authorize_action(g.user['uid'], Operation.RENEW, domain_name)
        dnsService.renew_domain(domain_name)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": e.msg}, 403
