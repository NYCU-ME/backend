from flask import Response, request, g
import re, ipaddress

from main import app, authService, dnsService
from services import Operation



domainRegex = re.compile(r'^([A-Za-z0-9]\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\.){1,3}[A-Za-z]{2,6}$')

def is_ip(addr, protocol = ipaddress.IPv4Address):
    try:
        ip = ipaddress.ip_address(addr)
        if isinstance(ip, protocol):
            return str(ip)
        return False
    except:
        return False

def is_domain(domain):
    return domainRegex.fullmatch(domain)

def check_type(type_, value):

    if type_ == 'A':
        if not is_ip(value, ipaddress.IPv4Address):
            return {"errorType": "DNSError", "msg": "Type A with non-IPv4 value."}, 403

        value = is_ip(value, ipaddress.IPv4Address)

    if type_ == 'AAAA':
        if not is_ip(value, ipaddress.IPv6Address):
            return {"errorType": "DNSError", "msg": "Type AAAA with non-IPv6 value."}, 403

        value = is_ip(value, ipaddress.IPv6Address)

    if type_ == 'CNAME' and not is_domain(value):
        return {"errorType": "DNSError", "msg": "Type CNAME with non-domain-name value."}, 403

    if type_ == 'MX' and not is_domain(value):
        return {"errorType": "DNSError", "msg": "Type MX with non-domain-name value."}, 403

    if type_ == 'TXT' and (len(value) > 255 or value.count('\n')):
        return {"errorType": "DNSError", "msg": "Type TXT with value longer than 255 chars or more than 1 line."}, 403

    return None


@app.route("/ddns/<path:domain>/records/<string:type_>/<string:value>", methods=['POST'])
def addRecord(domain, type_, value):

    if not g.user:
        return {"message": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name   = '.'.join(reversed(domain_struct))

    try:
        req = request.json
        if req and 'ttl' in req and req['ttl'].isnumeric() and 5 <= int(req['ttl']) <= 86400:
            ttl = int(req['ttl'])
        else:
            ttl = 5
    except:
        ttl = 5

    check_result = check_type(type_, value)
    if check_result:
        return check_result

    try:
        authService.authorize_action(g.user['uid'], Operation.MODIFY, domain_name)
        dnsService.add_record(domain_name, type_, value, ttl)
        return {"msg": "ok"}
    except Exception as e:
        return {"error": e.msg}, 403

@app.route("/ddns/<path:domain>/records/<string:type_>/<string:value>", methods=['DELETE'])
def delRecord(domain, type_, value):

    if not g.user:
        return {"message": "Unauth."}, 401

    domain_struct = domain.lower().strip('/').split('/')
    domain_name   = '.'.join(reversed(domain_struct))

    check_result = check_type(type_, value)
    if check_result:
        return check_result

    try:
        authService.authorize_action(g.user['uid'], Operation.MODIFY, domain_name)
        dnsService.del_record(domain_name, type_, value)
        return {"msg": "ok"}
    except Exception as e:
        return {"error": e.msg}, 403
