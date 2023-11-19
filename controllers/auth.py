from flask import Response, request
from main import app, g, nycu_oauth, authService

@app.route("/oauth/<string:code>", methods = ['GET'])
def get_token(code):

    token = nycu_oauth.get_token(code)
    if token:
        return {"token": authService.issue_token(nycu_oauth.get_profile(token))}
    else:
        return {"message": "Invalid code."}, 401
