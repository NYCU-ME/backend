import datetime
from flask import g
from main import app, authService, dnsService, elastic
from services import Operation

@app.route("/metrics/", methods=['GET'])
def get_metrics():
    num_of_user   = authService.count_user()
    num_of_domain = dnsService.count_domain()
    return {
        'num_of_user': num_of_user,
        'num_of_domain': num_of_domain
    }

@app.route("/traffic/<path:domain>", methods=['GET'])
def get_domain_traffic(domain):
    if not g.user:
        return {"msg": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name = '.'.join(reversed(domain_struct))

    result = []
    today = datetime.date.today()

    try:
        if not g.user['isAdmin']:
            authService.authorize_action(g.user['uid'], Operation.MODIFY, domain_name)
        for i in range(29, -1, -1):
            past_date = today - datetime.timedelta(days=i)
            date = past_date.strftime("%Y-%m-%d")
            result.append((date, elastic.query(domain_name, date)))

        return {"msg": "ok", "data": result}
    except Exception as e:
        return {"msg": str(e)}, 403
