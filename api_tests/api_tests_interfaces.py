import unittest, os, binascii

import string
import random
import time

from random import randint

from nose.plugins.attrib import attr

from api_interface.api_interface import APIInterface
from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_factomd import APIObjectsFactomd
from helpers.helpers import create_random_string, read_data_from_json

@attr(fast=True)
class ApiTestsWallet(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.interface = APIInterface()
        self.wallet_api_objects = APIObjectsWallet()
        self.api_objects = APIObjectsFactomd()
        self.first_address = self.wallet_api_objects.import_address_by_secret(self.data['factoid_wallet_address'])
        # self.second_address = self.wallet_api_objects.generate_factoid_address()
        # self.ecrate = self.api_objects.get_entry_credits_rate()
        self.entry_creds_wallet = self.wallet_api_objects.import_address_by_secret(self.data['ec_wallet_address'])
        # self.entry_creds_wallet2 = self.wallet_api_objects.generate_ec_address()

    def test_create_chain(self):
        # external ids must be in hex

        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        external_ids = [name_1, name_2]

        # content must be in hex
        content = binascii.hexlify(create_random_string(randint(100, 5000)))

        # compose chain
        transaction = self.interface.compose_chain(external_ids, content, self.entry_creds_wallet)
        self.api_objects.submit_factoid_by_transaction(transaction)
        self.api_objects.get_pending_entries()

    def test_allocate_funds_to_factoid_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        result = self.api_objects.submit_factoid_by_transaction(transaction)
        self.assertIn("Successfully submitted", result['message'], 'Factoid transaction not successful')

        # chain id for factoid transaction is always 000...f, abbreviated to just f
        for x in range(0, 300):
            status = self.api_objects.get_status(result['txid'], 'f')['status']
            if (status == 'TransactionACK'):
                break
            time.sleep(1)
        self.assertLess(x, 299, 'Factoid transaction not acknowledged within 5 minutes')

    def test_allocate_not_enough_funds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))


        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 1)
        self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 1)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)

        self.assertTrue('Error totalling Outputs: Amount is out of range' in
                        self.wallet_api_objects.sign_transaction(transaction_name)['error']['data'])

    def test_list_transactions_api_call(self):
        self.assertTrue('transactions' in self.wallet_api_objects.list_all_transactions_in_factoid_blockchain(),
                        'Transactions are not listed')

    def test_list_transaction_by_id(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        txid = self.api_objects.submit_factoid_by_transaction(transaction)['txid']
        wait_for_ack(txid)
        self.assertTrue(self.wallet_api_objects.list_transactions_by_txid(txid)['transactions'][0]['inputs'][0]['amount'] == 100000000, 'Transaction is not listed')

    def test_list_current_working_transactions_in_wallet(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

    def test_delete_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

        self.wallet_api_objects.delete_transaction(transaction_name)
        self.assertFalse(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_entry_credit_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.api_objects.submit_factoid_by_transaction(transaction)['message'])

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_entry_credit_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.api_objects.submit_factoid_by_transaction(transaction)['message'])
        self.api_objects.get_pending_transactions()

    def create_chain_new(self, external_ids, content, ecpub):
        self.wallet_api_objects.compose_chain_new(self, external_ids, content, ecpub)

