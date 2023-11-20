from flask import Response, request
from main import app, g, nycu_oauth, authService


@app.before_request
def before_request():
    
    g.user = authService.authenticate_token(request.headers.get('Authorization'))

@app.route("/oauth/<string:code>", methods = ['GET'])
def get_token(code):
    
    token = nycu_oauth.get_token(code)

    if token:
        return {"token": authService.issue_token(nycu_oauth.get_profile(token))}
    else:
        return {"message": "Invalid code."}, 401

@app.route("/whoami/", methods = ['GET'])
def whoami():

    if g.user:
        data = {}
        data['uid'] = g.user['uid']
        data['email'] = g.user['email']
        return data
    
    return {"message": "Unauth."}, 401
