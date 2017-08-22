import requests
import json

from helpers.helpers import read_data_from_json


class ApiObjectsDebug():
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    def change_factomd_address(self, value):
         self.factomd_address = value

    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://'+self.factomd_address+'/debug'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text, r.status_code

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/debug'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text


    def get_federated_servers(self):
        '''
        Get the list of the federated servers
        :return: the list of federated servers
        '''
        federated_servers = json.loads(self.send_get_request_with_method('federated-servers'))
        return federated_servers["result"]["FederatedServers"]

    def get_audit_servers(self):
        '''
        Get the list of the audit servers
        :return: the list of audit servers
        '''
        audit_servers = json.loads(self.send_get_request_with_method('audit-servers'))
        return audit_servers["result"]["AuditServers"]