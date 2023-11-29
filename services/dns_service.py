import time
import re
from enum import Enum


DOMAIN_REGEX = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")

class DNSErrors(Enum):
    NXDOMAIN             = "Non-ExistentDomain"
    DUPLICATED           = "DuplicatedRecord"
    UNALLOWED            = "NotAllowedOperation" 

class DNSError(Exception):
    def __init__(self, typ, msg = ""):
        self.typ = str(typ)
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "%s: %s" % (self.typ, self.msg)

class DNSService():
    def __init__(self, logger, users, domains, records, ddns, host_domains):
        self.logger  = logger
        self.users = users
        self.domains = domains
        self.records = records
        self.ddns = ddns
        self.host_domains = host_domains

    def check_domain(self, domain_name):
        domain_struct = list(reversed(domain_name.split('.')))

        for p in domain_struct:
            if not DOMAIN_REGEX.fullmatch(p):
                return 0

        def is_match(rule, struct):
            # Check if the domain is matching to a specific rule
            rule = list(reversed(rule.split('.')))
            if len(rule) > len(struct):
                return 0
            
            for i in range(len(rule)):
                if rule[i] == '*':
                    return i + 1
                elif rule[i] != struct[i]:
                    return 0

        for domain in self.host_domains:
            if (x:=is_match(domain, domain_struct)):
                return x

    def get_domain(self, domain_name):
        domain = self.domains.get_domain(domain_name)
        if not domain:
            return None

        domain_info = {}
        domain_info['id'] = domain.id
        domain_info['regDate'] = domain.regDate
        domain_info['expDate'] = domain.expDate
        domain_info['domain'] = domain_name
        domain_info['records'] = []
        records = self.records.get_records(domain.id)
        for record in records:
            domain_info['records'].append((record.id,
                                           record.type,
                                           record.value,
                                           record.ttl))
        return domain_info

    def get_expired_domain(self):
        return self.domains.get_expired_domain()

    def list_domains_by_user(self, uid):
        domains = []
        for domain in self.domains.list_by_user(uid):
            domain_info = self.get_domain(domain.domain)
            domains.append(domain_info)    
        return domains

    def register_domain(self, uid, domain_name):
        if not self.check_domain(domain_name):
            raise DNSError(DNSErrors.UNALLOWED, "This domain is not hosted by us.")
        domain = self.domains.get_domain(domain_name)
        if domain:
            raise DNSError(DNSErrors.UNALLOWED, "This domain have been registered.")
        self.domains.register(domain_name, uid)

    def renew_domain(self, domain_name):
        domain = self.domains.get_domain(domain_name)
        if not domain:
            raise DNSError(DNSErrors.NXDOMAIN, "This domain is not registered.")
        self.domains.renew(domain_name)

    def release_domain(self, domain_name):
        domain = self.domains.get_domain(domain_name)
        if not domain:
            raise DNSError(DNSErrors.NXDOMAIN, "This domain is not registered.")
        records = self.records.get_records(domain.id)
        for record in records:
            self.del_record_by_id(record.id)
        self.domains.release(domain_name)

    def add_record(self, domain_name, type_, value, ttl):
        domain = self.domains.get_domain(domain_name)
        if not domain:
            raise DNSError(DNSErrors.NXDOMAIN, "This domain is not registered.")

        records = self.records.get_records(domain.id)
        for record in records:
            if type_ == record.type and value == record.value:
                raise DNSError(DNSErrors.DUPLICATED, "You have created same record.")

        self.records.add_record(domain.id, type_, value, ttl)
        self.ddns.add_record(domain_name, type_, value, ttl)
    
    def del_record(self, domain_name, type_, value):
        domain_id = self.domains.get_domain(domain_name).id
        record = self.records.get_record_by_type_value(domain_id,
                                                       type_,
                                                       value)
        if not record:
            raise DNSError(DNSErrors.UNALLOWED, "This record does not exist.")
        self.del_record_by_id(record.id)

    def del_record_by_id(self, record_id):
        record = self.records.get_record(record_id)
        if not record:
            raise DNSError(DNSErrors.UNALLOWED, "This record does not exist.")

        domain = self.domains.get_domain_by_id(record.domain)
        self.records.del_record_by_id(record_id)
        self.ddns.del_record(domain.domain, record.type, record.value)
