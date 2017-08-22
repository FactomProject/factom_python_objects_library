import requests
import json

from helpers.helpers import read_data_from_json


class APIObjectsWallet():

    data = read_data_from_json('addresses.json')
    wallet_address = data['wallet_address']

    def send_post_request_with_params_dict(self, method, params_dict):
        url = 'http://'+ self.wallet_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        print data
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://' + self.wallet_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        print data
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def send_get_request_with_method(self, method):
        url = 'http://' + self.wallet_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def check_address_by_public_address(self, address):
        '''
        Import address by public address
        :param address: str
        :return: secret address
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('address', {'address': address}))
        return blocks["result"]["secret"]

    def check_all_addresses(self):
        '''
        Import all addresses from wallet
        :return: list of dicts, addresses
        '''
        blocks = json.loads(self.send_get_request_with_method('all-addresses'))
        return blocks['result']['addresses']

    def generate_ec_address(self):
        '''
        Generate ec addresses
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_method('generate-ec-address'))
        return blocks['result']['public']

    def generate_factoid_address(self):
        '''
        Generate ec addresses
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_method('generate-factoid-address'))
        return blocks['result']['public']

    def import_address_by_secret(self, secret_address):
        '''
        Imports addres by secret addres and returns public
        :param secret_address: str
        :return: str, public addresss
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('import-addresses', {'addresses': [{'secret': secret_address}]}))
        return blocks['result']['addresses'][0]['public']

    def import_mnemonic(self, words):
        '''
        Import from mnemonics
        :param words: string 12 words
        :return: json
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('import-mnemonic', {'words': words}))
        return blocks#["result"]["public"]

    def list_all_transactions_in_factoid_blockchain(self):
        '''
        List all transactions
        :return: json, transactions
        '''
        blocks = json.loads(self.send_get_request_with_method('transactions'))
        return blocks["result"]

    def list_transactions_by_txid(self, txid):
        '''

        :param txid: str
        :return:
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'txid': txid}))
        return blocks["result"]

    def list_transactions_by_address(self, address):
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'address': address}))
        return blocks["result"]

    def list_transactions_by_range(self, start, end):
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'range': {'start': start, "end": end}}))
        return blocks["result"]

    def create_new_transaction(self, transaction_name):
        '''
        Create new transaction
        :param transaction_name: str - name
        :return: transaction
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('new-transaction', {'tx-name': transaction_name}))
        return blocks["result"]

    def list_current_working_transactions_in_wallet(self):
        blocks = self.send_get_request_with_method('tmp-transactions')
        return blocks

    def delete_transaction(self, transaction_name):
        blocks = json.loads(self.send_post_request_with_params_dict('delete-transaction', {'tx-name': transaction_name}))
        return blocks["result"]

    def add_input_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-input', {'tx-name': transaction_name,
                                                                                 'address':address,'amount': amount}))
        return blocks#["result"]

    def add_output_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-output', {'tx-name': transaction_name,
                                                                                 'address': address, 'amount': amount}))
        return blocks["result"]

    def add_entry_credit_output_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-ec-output', {'tx-name': transaction_name,
                                                                                 'address': address, 'amount': amount}))
        return blocks["result"]

    def add_fee_to_transaction(self, transaction_name, address):
        blocks = json.loads(self.send_post_request_with_params_dict('add-fee', {'tx-name': transaction_name,
                                                                                 'address': address}))
        return blocks["result"]

    def subtract_fee_from_transaction(self, transaction_name, address):
        blocks = json.loads(self.send_post_request_with_params_dict('sub-fee', {'tx-name': transaction_name,
                                                                               'address': address}))
        return blocks

    def sign_transaction(self, transaction_name):
        blocks = json.loads(self.send_post_request_with_params_dict('sign-transaction', {'tx-name': transaction_name}))
        return blocks

    def compose_chain_new(self, external_ids, content, ecpub):
        blocks = json.loads(self.send_post_request_with_params_dict('compose-chain',
                 {'chain': {'firstentry': {'extids': external_ids, 'content': content}}, 'ecpub': ecpub}))
        return blocks

    def compose_chain(self, external_ids, content, ecpub):
        blocks = json.loads(self.send_post_request_with_params_dict('compose-chain',
                 {'chain': {'firstentry': {'extids': external_ids, 'content': content}}, 'ecpub': ecpub}))
        return blocks['result']['commit']['params']['message'], blocks['result']['reveal']['params']['entry']

    def compose_transaction(self, transaction_name):
        blocks = json.loads(self.send_post_request_with_params_dict('compose-transaction',
                                                                    {'tx-name': transaction_name}))
        return blocks["result"]['params']['transaction']

    def get_wallet_height(self):
        blocks = json.loads(self.send_get_request_with_method('get-height'))
        return blocks["result"]