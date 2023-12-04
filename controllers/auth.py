from flask import request, g
from main import env_test, app, nycu_oauth, authService, dnsService
import config

@app.before_request
def before_request():

    g.user = authService.authenticate_token(request.headers.get('Authorization'))

    extra = {
        'remote_addr': request.remote_addr, 
        'url': request.url
    }
    app.logger.info('Logged in', extra=extra)

@app.route("/oauth/<string:code>", methods = ['GET'])
def get_token(code):

    token = nycu_oauth.get_token(code)
    if token:
        return {'token': authService.issue_token(nycu_oauth.get_profile(token))}
    else:
        return {'msg': "Invalid code."}, 401

@app.route("/test_auth/", methods = ['GET'])
def get_token_for_test():

    if env_test:
        return {'msg': 'ok', 'token': authService.issue_token(request.json)}
    else:
        return {'msg': "It is not currently running on testing mode."}, 401

@app.route("/whoami/", methods = ['GET'])
def whoami():
    if g.user:
        data = {}
        data['uid'] = g.user['uid']
        data['email'] = g.user['email']
        data['domains'] = dnsService.list_domains_by_user(g.user['uid'])
        return data
    return {"msg": "Unauth."}, 401
