import time
from enum import Enum


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
    def __init__(self, logger, users, domains, records, ddns):
        self.logger  = logger
        self.users = users
        self.domains = domains
        self.records = records
        self.ddns = ddns

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

    def register_domain(self, uid, domain_name):
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
            self.del_record(record.id)
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

    def del_record(self, record_id):
        record = self.records.get_record(record_id)
        if not record:
            raise DNSError(DNSErrors.UNALLOWED, "This record does not exist.")

        domain = self.domains.get_domain_by_id(record.domain_id)
        self.records.del_record(record_id)
        self.ddns.del_record(domain.domain, record.type, record.value)
