from flask import request, g
from main import env_test, app, nycu_oauth, authService, dnsService, mailService, BASE_URL

@app.before_request
def before_request():

    g.user = authService.authenticate_token(request.headers.get('Authorization'))
    if g.user and g.user['type'] != "logged":
        g.user = None

    extra = {
        'remote_addr': request.remote_addr, 
        'url': request.url
    }
    app.logger.info("Logged in", extra=extra)

@app.route("/oauth/<string:code>", methods = ['GET'])
def get_token(code):

    token = nycu_oauth.get_token(code)
    if token:
        return {'token': authService.issue_token(nycu_oauth.get_profile(token), "logged")}
    return {'msg': "Invalid code."}, 401

@app.route("/test_auth/", methods = ['GET'])
def get_token_for_test():

    if env_test:
        return {'msg': "ok", 'token': authService.issue_token(request.json, "logged")}
    return {'msg': "It is not currently running on testing mode."}, 401

@app.route("/whoami/", methods = ['GET'])
def whoami():
    if g.user:
        data = {}
        data['uid'] = g.user['uid']
        data['email'] = g.user['email']
        data['domains'] = dnsService.list_domains_by_user(g.user['uid'])
        return data
    return {'msg': "Unauth."}, 401

@app.route("/login_email", methods=['POST'])
def login_email():
    try:
        data = request.json
        if 'email' not in data:
            return  {"msg": "Invalid data."}, 400
    except Exception:
        return {"msg": "Invalid data."}, 400

    if not authService.verify_email(data['email']):
        return {"msg": "Invalid email."}, 400

    # passwd = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    # hashed_passwd = bcrypt.hashpw(passwd.encode(), bcrypt.gensalt())
    # users.update_passwd(data['email'], hashed_passwd.decode())
    token = authService.issue_token(
        {
            'email'   : data['email'],
            'username': data['email']
        },
        "logged"
    )

    mailService.send_mail(data['email'], "NYCU-ME 登入鏈結", f"{BASE_URL}login_email/?token={token}")
    return {'msg': 'ok'}
