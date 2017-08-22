from api_objects.api_objects_debug import ApiObjectsDebug
import unittest
import re
from helpers.helpers import read_data_from_json
from nose.plugins.attrib import attr

@attr(api=True)
class FactomDebugAPItests(unittest.TestCase):

    def setUp(self):
        self.factomd_debug_api = ApiObjectsDebug()
        data = read_data_from_json('addresses.json')
        self.factomd_address = data['factomd_address']
        self.controlpanel = read_data_from_json('faulting.json')


    def test_get_federated_servers(self):
        self.factomd_debug_api.change_factomd_address(self.factomd_address)
        federated_servers = self.factomd_debug_api.get_federated_servers()
        self.assertFalse(re.search('Method not found',str(federated_servers)), "get federated server method is not found")
        fed_list = []
        for fedservers in federated_servers:
            for server in fedservers.values():
                if re.search((r'.{64}$'),str(server)):
                    fed_list.append(server)
        return fed_list

    def test_get_audit_servers(self):
        audit_servers = self.factomd_debug_api.get_audit_servers()
        self.assertFalse(re.search('Method not found',str(audit_servers)), "get audit server method is not found")
        audit_list = []
        for auditservers in audit_servers:
            for server in auditservers.values():
                if re.search((r'.{64}$'), str(server)):
                    audit_list.append(server)
        return audit_list
