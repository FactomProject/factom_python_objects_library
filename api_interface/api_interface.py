import unittest, os, binascii, json, requests, ast

import string
import random
import time

from random import randint

from nose.plugins.attrib import attr

from api_objects.api_objects_interface import APIObjectsInterface

from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_factomd import APIObjectsFactomd
from helpers.helpers import create_random_string, read_data_from_json

@attr(fast=True)
class APIInterface():
    # data = read_data_from_json('shared_test_data.json')
    data = read_data_from_json('addresses.json')
    wallet_address = data['wallet_address']
    factomd_address = data['factomd_address']

    def setUp(self):
        self.api_objects_interface = APIObjectsInterface

        self.api_objects_wallet = APIObjectsWallet()
        self.api_objects_factomd = APIObjectsFactomd()
        # self.first_address = self.api_objects_interface.import_addresses(self.data['factoid_wallet_address'], self.data['ec_wallet_address'])
        # self.second_address = self.wallet_api_objects.generate_factoid_address()
        # self.ecrate = self.api_objects.get_entry_credits_rate()
        # self.entry_creds_wallet = self.api_objects_wallet.import_address_by_secret(self.data['ec_wallet_address'])
        # self.entry_creds_wallet2 = self.wallet_api_objects.generate_ec_address()

        '''
        For all three 'send requests' below:
        :param destination: if 'wallet' then the API call will be sent to the factom-walletd port (8089)
        else the API call will be sent to the factomd port (8088)
        :param method: name of the API method to call
        :param params_dict: dictionary containing the parameters to be sent with the API call
        :return: result of the API call
        '''

    def send_post_request_with_params_dict(self, destination, method, params_dict):
        address = self.wallet_address if destination == 'wallet' else self.factomd_address
        url = 'http://'+ address +'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        print data
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def send_get_request_with_params_dict(self, destination, method, params_dict):
        address = self.wallet_address if destination == 'wallet' else self.factomd_address
        url = 'http://' + address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def send_get_request_with_method(self, destination, method):
        address = self.wallet_address if destination == 'wallet' else self.factomd_address
        url = 'http://' + address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def create_chain(self, external_ids, content, ec_address):
        '''
         Create a new chain
         :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
         :param content: str, the content (in hex) of the 1st entry of the chain
         :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
         :return str of resultant chain data in the form:
          txid: <txid>
          entryhash: <entryhash>
          chainid: <chainid>
         '''
        transaction = self.compose_chain(external_ids, content, ec_address)
        commit = self.commit_chain(transaction['result']['commit']['params']['message'])
        print 'commit', commit
        reveal = self.reveal_chain(transaction['result']['reveal']['params']['entry'])
        # self.get_pending_entries()
        print 'txid', commit[1]
        commit1 = commit[1]
        txid = 'txid: ' + commit1['txid']  + '\n'
        entryhash = 'entryhash: ' + commit[1]['entryhash']  + '\n'
        chainid = 'chainid: ' + commit[1]['chainid']
        return txid + entryhash + chainid

    def compose_chain(self, external_ids, content, ec_address):
        '''
        Create both the 'commit-chain' JSON and the 'reveal-chain' JSON that can then be sent in API calls to create a chain at a later time
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
        :param content: str, the content (in hex) of the 1st entry of the chain
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
        :return blocks: JSON of the two API calls (commit and reveal) that when sent later will actually create the chain
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('wallet', 'compose-chain', {'chain': {'firstentry': {'extids': external_ids, 'content': content}}, 'ecpub': ec_address}))
        return blocks

    def commit_chain(self, message):
        '''
        Commit chain by message
        :param message: str, the message portion of the API call
        :return success: binary indicating whether or not the  commit API call succeeded
        :return blocks['error']: if the API call failed, the contents of the 'error' JSON block
        :return blocks['result']: if the API call succeeded, the contents of the 'result' JSON block
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('factomd', 'commit-chain', {'message': message}))
        if 'error' in blocks:
            success = False
            return success, blocks['error']
        else:
            success = True
            return success, blocks['result']

    def reveal_chain(self, entry):
        '''
        Reveal chain by entry
        :param entry: str, the entry portion of the API call
        :return: blocks['result'] the contents of the 'result' JSON block
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('factomd', 'reveal-chain', {'entry': entry}))
        return blocks['result']

    def get_pending_entries(self):
        '''
        Get all pending entries
        Note: an entry may not be available as pending immediately after creation. Some wait time may be necessary.
        :return: json containing EntryHash and ChainID
        '''
        blocks = json.loads(self.send_get_request_with_method('factomd', 'pending-entries'))
        return blocks['result']

    def create_entry(self, chain_id, external_ids, content, ec_address):
        '''
         Create a new entry in an existing chain
         :param chain_id: str, chain ID of existing chain
         :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
         :param content: str, the content (in hex) of the 1st entry of the chain
         :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
         :return str of resultant chain data in the form:
          txid: <txid>
          entryhash: <entryhash>
          chainid: <chainid>
         '''
        transaction = self.compose_entry(external_ids, content, ec_address)
        commit = self.commit_chain(transaction['result']['commit']['params']['message'])
        print 'commit', commit
        reveal = self.reveal_chain(transaction['result']['reveal']['params']['entry'])
        # self.get_pending_entries()
        print 'txid', commit[1]
        commit1 = commit[1]
        txid = 'txid: ' + commit1['txid']  + '\n'
        entryhash = 'entryhash: ' + commit[1]['entryhash']  + '\n'
        chainid = 'chainid: ' + commit[1]['chainid']
        return txid + entryhash + chainid





















    def submit_factoid_transaction(self, transaction):
        '''
        Submit factoid
        :param transaction: str, transaction hash
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('factoid-submit', {'transaction':
                                                                                          transaction}))
        return blocks
        # return blocks['result']

    def test_allocate_funds_to_factoid_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.api_objects_wallet.create_new_transaction(transaction_name)
        self.api_objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.api_objects_wallet.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.api_objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.api_objects_wallet.sign_transaction(transaction_name)
        transaction = self.api_objects_wallet.compose_transaction(transaction_name)
        result = self.api_objects_factomd.submit_factoid_by_transaction(transaction)
        self.assertIn("Successfully submitted", result['message'], 'Factoid transaction not successful')

        # chain id for factoid transaction is always 000...f, abbreviated to just f
        for x in range(0, 300):
            status = self.api_objects_factomd.get_status(result['txid'], 'f')['status']
            if (status == 'TransactionACK'):
                break
            time.sleep(1)
        self.assertLess(x, 299, 'Factoid transaction not acknowledged within 5 minutes')

    def test_allocate_not_enough_funds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))


        self.api_objects_wallet.create_new_transaction(transaction_name)
        self.api_objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 1)
        self.api_objects_wallet.add_output_to_transaction(transaction_name, self.second_address, 1)
        self.api_objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)

        self.assertTrue('Error totalling Outputs: Amount is out of range' in
                        self.api_objects_wallet.sign_transaction(transaction_name)['error']['data'])

    def test_list_transactions_api_call(self):
        self.assertTrue('transactions' in self.api_objects_wallet.list_all_transactions_in_factoid_blockchain(),
                        'Transactions are not listed')

    def test_list_transaction_by_id(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.api_objects_wallet.create_new_transaction(transaction_name)
        self.api_objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.api_objects_wallet.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.api_objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.api_objects_wallet.sign_transaction(transaction_name)
        transaction = self.api_objects_wallet.compose_transaction(transaction_name)
        txid = self.api_objects_factomd.submit_factoid_by_transaction(transaction)['txid']
        wait_for_ack(txid)
        self.assertTrue(self.api_objects_wallet.list_transactions_by_txid(txid)['transactions'][0]['inputs'][0]['amount'] == 100000000, 'Transaction is not listed')

    def test_list_current_working_transactions_in_wallet(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.api_objects_wallet.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.api_objects_wallet.list_current_working_transactions_in_wallet())

    def test_delete_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.api_objects_wallet.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.api_objects_wallet.list_current_working_transactions_in_wallet())

        self.api_objects_wallet.delete_transaction(transaction_name)
        self.assertFalse(transaction_name in self.api_objects_wallet.list_current_working_transactions_in_wallet())

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.api_objects_wallet.create_new_transaction(transaction_name)
        self.api_objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.api_objects_wallet.add_entry_credit_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.api_objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.api_objects_wallet.sign_transaction(transaction_name)
        transaction = self.api_objects_wallet.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.api_objects_factomd.submit_factoid_by_transaction(transaction)['message'])

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.api_objects_wallet.create_new_transaction(transaction_name)
        self.api_objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.api_objects_wallet.add_entry_credit_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.api_objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.api_objects_wallet.sign_transaction(transaction_name)
        transaction = self.api_objects_wallet.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.api_objects_factomd.submit_factoid_by_transaction(transaction)['message'])
        self.api_objects_factomd.get_pending_transactions()

    def create_chain_new(self, external_ids, content, ecpub):
        self.api_objects_wallet.compose_chain_new(self, external_ids, content, ecpub)

