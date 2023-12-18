import re
from enum import Enum

DOMAIN_REGEX = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")

class DNSErrors(Enum):
    NXDOMAIN = "Non-ExistentDomain"
    DUPLICATED = "DuplicatedRecord"
    UNALLOWED = "NotAllowedOperation"

class DNSError(Exception):
    def __init__(self, typ, msg=""):
        self.typ = str(typ)
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return f"{self.typ}: {self.msg}"

class DNSService():
    def __init__(self, logger, users, domains, records, glues, ddns, host_domains):
        self.logger  = logger
        self.users = users
        self.domains = domains
        self.records = records
        self.glues = glues
        self.ddns = ddns
        self.host_domains = host_domains

    def __get_domain_info(self, domain):
        domain_info = {}
        domain_info['id'] = domain.id
        domain_info['regDate'] = domain.regDate
        domain_info['expDate'] = domain.expDate.strftime('%Y-%m-%d')
        domain_info['domain'] = domain.domain
        domain_info['records'] = []
        domain_info['glues'] = []
        records = self.records.get_records(domain.id)
        glues = self.glues.get_records(domain.id)
        for record in records:
            domain_info['records'].append((record.id,
                                           record.type,
                                           record.value,
                                           record.ttl))
        for record in glues:
            domain_info['glues'].append((record.id,
                                         record.subdomain,
                                         record.type,
                                         record.value,
                                         record.ttl))
        return domain_info

    def check_domain(self, domain_name):
        domain_struct = list(reversed(domain_name.split('.')))

        for p in domain_struct:
            if not DOMAIN_REGEX.fullmatch(p):
                return 0

        def is_match(rule, struct):
            rule = list(reversed(rule.split('.')))
            if len(rule) > len(struct):
                return 0

            for i, element in enumerate(rule):
                if element == '*':
                    return i + 1
                if element != struct[i]:
                    return 0

            return None

        for domain in self.host_domains:
            match_result = is_match(domain, domain_struct)
            if match_result is not None:
                return match_result

        return None

    def get_domain(self, domain_name):
        domain = self.domains.get_domain(domain_name)
        if not domain:
            return None

        domain_info = self.__get_domain_info(domain)
        return domain_info

    def get_domain_by_id(self, idx):
        domain = self.domains.get_domain_by_id(idx)
        if not domain:
            return None

        domain_info = self.__get_domain_info(domain)
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
        glues = self.glues.get_records(domain.id)
        for record in records:
            self.del_record_by_id(record.id)
        for record in glues:
            self.del_glue_record(domain.domain, record.subdomain, record.type, record.value)
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

    def add_glue_record(self, domain_name, subdomain, type_, value, ttl):
        domain = self.domains.get_domain(domain_name)
        real_domain = f"{subdomain}.{domain_name}"
        self.glues.add_record(domain.id, subdomain, type_, value, ttl)
        self.ddns.add_record(real_domain, type_, value, ttl)

    def del_glue_record(self, domain_name, subdomain, type_, value):
        domain = self.domains.get_domain(domain_name)
        real_domain = f"{subdomain}.{domain_name}"
        glue_record = self.glues.get_record_by_type_value(
                domain.id,
                subdomain,
                type_,
                value
        )
        self.glues.del_record(glue_record.id)
        self.ddns.del_record(real_domain, type_, value)

    def list_domains(self):
        domains = self.domains.list_all()
        result = []
        for domain in domains:
            result.append(self.__get_domain_info(domain))
        return result
