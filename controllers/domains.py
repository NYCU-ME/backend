from flask import Response, request
from main import app, g, authService


@app.route("/domains/<path:domain>", methods=['POST'])
def applyDomain(domain):
    
    if not g.user:
        return {"message": "Unauth."}, 401
    
	user         = users.getUser(g.user['uid'])
    domainStruct = domain.lower().strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)
 	
	
