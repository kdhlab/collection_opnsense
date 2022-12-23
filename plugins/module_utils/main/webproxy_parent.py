from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.main import \
    validate_int_fields, simplify_translate, is_ip
from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.cls import BaseModule


class Parent(BaseModule):
    CMDS = {
        'set': 'set',
        'search': 'get',
    }
    API_KEY_1 = 'proxy'
    API_KEY_2 = 'general'
    API_KEY = 'parentproxy'
    API_MOD = 'proxy'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'host', 'auth', 'user', 'password', 'port', 'local_domains', 'local_ips',
        'enabled',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TRANSLATE = {
        'auth': 'enableauth',
        'local_domains': 'localdomains',
        'local_ips': 'localips',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'auth'],
        'list': ['local_domains', 'local_ips'],
        'int': ['port'],
    }
    INT_VALIDATIONS = {
        'port': {'min': 1, 'max': 65535},
    }
    STR_VALIDATIONS = {
        'user': r'^([0-9a-zA-Z\._\-]){1,32}$',
        'password': r'^([0-9a-zA-Z\._\-]){1,32}$',
    }
    FIELDS_DIFF_EXCLUDE = ['password']
    EXIST_ATTR = 'settings'
    TIMEOUT = 60.0

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session)
        self.settings = {}
        self.call_cnf = {
            'module': self.API_MOD,
            'controller': self.API_CONT,
        }
        self.s = Session(
            module=module,
            timeout=self.TIMEOUT,
        ) if session is None else session

    def check(self):
        if self.p['enabled']:
            if self.p['host'] == '' or self.p['port'] == '':
                self.m.fail_json('To enable a parent proxy, a host and port must be provided!')

            if not is_ip(self.p['host']):
                self.m.fail_json(f"Provided host '{self.p['host']}' is not a valid IP-Address!")

        validate_int_fields(module=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        self.settings = self._search_call()
        self.r['diff']['before'] = self.b.build_diff(self.settings)
        self.r['diff']['after'] = self.b.build_diff({
            k: v for k, v in self.p.items() if k in self.settings
        })

    def _search_call(self) -> dict:
        settings = self.s.get(cnf={
            **self.call_cnf, **{'command': self.CMDS['search']}
        })[self.API_KEY_1][self.API_KEY_2][self.API_KEY]

        return simplify_translate(
            existing=settings,
            typing=self.FIELDS_TYPING,
            translate=self.FIELDS_TRANSLATE,
        )

    def get_existing(self) -> dict:
        return self._search_call()

    def _build_request(self) -> dict:
        return {self.API_KEY_1: {self.API_KEY_2: self.b.build_request()}}

    def update(self):
        self.b.update(enable_switch=False)