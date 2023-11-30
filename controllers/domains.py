from flask import g
import datetime
from main import app, authService, dnsService, elastic
from services import Operation

@app.route("/domains/<path:domain>", methods=['POST'])
def register_domain(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.replace('.', '/').lower().strip('/').split('/')
    domain_name = '.'.join(reversed(domain_struct))

    if len(domain_struct[-1]) < 4:
        return {"msg": "Length must be greater than 3."}, 400

    if dnsService.check_domain(domain_name) != len(domain_struct):
        return {"msg": "You can only register specific level domain name."}, 400

    try:
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
        authService.authorize_action(g.user['uid'], Operation.RENEW, domain_name)
        dnsService.renew_domain(domain_name)
        return {"msg": "ok"}
    except Exception as e:
        return {"msg": str(e)}, 403

@app.route("/traffic/<path:domain>", methods=['GET'])
def get_domain_traffic(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name = '.'.join(reversed(domain_struct))
    data = []
    try:
        authService.authorize_action(g.user['uid'], Operation.MODIFY, domain_name)
        today = datetime.date.today()
        for i in range(30, 0, -1):
            past_date = today - datetime.timedelta(days=i)
            date = past_date.strftime("%Y-%m-%d")
            data.append(elastic.query_logs_count_by_data(domain_name, date))
        return {"msg": "ok", "data": data}
    except Exception as e:
        return {"msg": str(e)}, 403


