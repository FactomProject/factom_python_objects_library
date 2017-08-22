import unittest
import string
import random
import time

from nose.plugins.attrib import attr

from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_factomd import APIObjectsFactomd
from helpers.helpers import read_data_from_json

@attr(stress_test=True)
class ApiTestsTransactions(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.wallet_api_objects = APIObjectsWallet()
        self.api_objects = APIObjectsFactomd()
        self.first_address = self.wallet_api_objects.import_address_by_secret(self.data['factoid_wallet_address'])
        self.second_address = self.wallet_api_objects.generate_factoid_address()
        self.entrycredit_address = self.wallet_api_objects.generate_ec_address()
        self.ecrate = self.api_objects.get_entry_credits_rate()

    def test_multiple_factoid_address_transactions(self):
        '''
        This testcase will submit 4 factoid transactions per second and checks for transaction status after one block time.
        :return: nothing. because the testcase only loads.
        special note  : this test case uses sleep to control the # of transaction input. waiting for acknowledgement causes ports to run out
            and test case fails
        '''
        blocktime = self.data['BLOCKTIME']
        txidlist = []
        for x in range(1,6000):
            for temp in range(1,blocktime):
                for y in range(1,5):
                    transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
                    self.wallet_api_objects.create_new_transaction(transaction_name)
                    self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
                    self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 100000000)
                    self.wallet_api_objects.add_fee_to_transaction(transaction_name, self.first_address)
                    self.wallet_api_objects.sign_transaction(transaction_name)
                    transaction = self.wallet_api_objects.compose_transaction(transaction_name)
                    txidlist.append(self.api_objects.submit_factoid_by_transaction(transaction)['txid'])
                time.sleep(1)
            time.sleep(blocktime)
            for txid in txidlist:
                status = self.api_objects.get_status(txid,'f')['status']
                self.assertEquals(status, 'DBlockConfirmed', 'Transaction = %s is still not confirmed' % txid)


    def test_multiple_entrycredit_address_transactions(self):
        '''
        This testcase will submit 4 entry credit transactions per second and checks for transaction status after one block time.
        return: nothing.  because the testcase only loads.
        special note  : this test case uses sleep to control the # of transaction input. waiting for acknowledgement causes ports to run out
            and test case fails
        '''
        blocktime = self.data['BLOCKTIME']
        txidlist = []
        for x in range(1, 6000):
            for temp in range(1, blocktime):
                for y in range(1, 5):
                    transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
                    self.wallet_api_objects.create_new_transaction(transaction_name)
                    self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
                    self.wallet_api_objects.add_entry_credit_output_to_transaction(transaction_name, self.entrycredit_address, 100000000)
                    self.wallet_api_objects.add_fee_to_transaction(transaction_name, self.first_address)
                    self.wallet_api_objects.sign_transaction(transaction_name)
                    transaction = self.wallet_api_objects.compose_transaction(transaction_name)
                    txidlist.append(self.api_objects.submit_factoid_by_transaction(transaction)['txid'])
                time.sleep(1)
            time.sleep(blocktime)
            for txid in txidlist:
                status = self.api_objects.get_status(txid, 'f')['status']
                self.assertEquals(status, 'DBlockConfirmed', 'Transaction = %s is still not confirmed' % txid)

    def test_buy_entrycredits(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_entry_credit_output_to_transaction(transaction_name, self.entrycredit_address,
                                                                       100000000)
        self.wallet_api_objects.add_fee_to_transaction(transaction_name, self.first_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
