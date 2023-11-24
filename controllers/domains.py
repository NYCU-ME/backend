from flask import Response, request, g
from main import app, authService, dnsService
from services import Operation

@app.route("/domains/<path:domain>", methods=['POST'])
def register_domain(domain):

    if not g.user:
        return {"message": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name   = '.'.join(reversed(domain_struct))

    #try:
    authService.authorize_action(g.user['uid'], Operation.APPLY, domain_name)
    dnsService.register_domain(g.user['uid'], domain_name)
    return {"msg": "ok"}
    #except Exception as e:
    #    return {"error": e.msg}, 403
