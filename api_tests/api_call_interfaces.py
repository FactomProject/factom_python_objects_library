import unittest, os, binascii, string, random, time

from random import randint

from nose.plugins.attrib import attr

from api_objects.api_objects_interface import APIObjectsInterface
from api_interface.api_interface import APIInterface

from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_factomd import APIObjectsFactomd
from helpers.helpers import create_random_string, read_data_from_json

@attr(fast=True)
class APICallInterface(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.objects_interface = APIObjectsInterface()
        self.interface = APIInterface()

        self.objects_wallet = APIObjectsWallet()
        self.objects_factomd = APIObjectsFactomd()
        public_keys = self.objects_interface.import_addresses(
            self.data['factoid_wallet_address'], self.data['ec_wallet_address'])
        self.first_address = public_keys[0]
        self.entry_creds_wallet = public_keys[1]
        self.second_address = self.objects_wallet.generate_factoid_address()
        self.ecrate = self.objects_factomd.get_entry_credits_rate()
        self.entry_creds_wallet2 = self.objects_wallet.generate_ec_address()

    def test_test(self):
        print 'self.first_address', self.first_address
        print 'self.entry_creds_wallet', self.entry_creds_wallet


    def test_call_create_chain(self):
        # external ids must be in hex
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        external_ids = [name_1, name_2]

        # content must be in hex
        content = binascii.hexlify(create_random_string(randint(100, 5000)))

        # create chain
        result = self.interface.create_chain(external_ids, content, self.entry_creds_wallet)
        print 'result', result

        # wait for pending entry to appear
        # for x in range(0, self.data['BLOCKTIME']):
        #     pending = self.interface.get_pending_entries()
        #     if 'TransactionACK' in str(pending): break
        #     time.sleep(1)

    def test_call_create_entry(self):
        # create chain
        # external ids must be in hex
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        external_ids = [name_1, name_2]

        # content must be in hex
        content = binascii.hexlify(create_random_string(randint(100, 5000)))

        # create chain
        self.interface.create_chain(external_ids, content, self.entry_creds_wallet)

        # wait for pending entry to appear
        for x in range(0, self.data['BLOCKTIME']):
            pending = self.interface.get_pending_entries()
            if 'TransactionACK' in str(pending): break
            time.sleep(1)

        # create entry
        self.interface.create_entry(external_ids, content, self.entry_creds_wallet)









    def test_allocate_funds_to_factoid_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.objects_wallet.create_new_transaction(transaction_name)
        self.objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.objects_wallet.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.objects_wallet.sign_transaction(transaction_name)
        transaction = self.objects_wallet.compose_transaction(transaction_name)
        result = self.objects_factomd.submit_factoid_by_transaction(transaction)
        self.assertIn("Successfully submitted", result['message'], 'Factoid transaction not successful')

        # chain id for factoid transaction is always 000...f, abbreviated to just f
        for x in range(0, 300):
            status = self.objects_factomd.get_status(result['txid'], 'f')['status']
            if (status == 'TransactionACK'):
                break
            time.sleep(1)
        self.assertLess(x, 299, 'Factoid transaction not acknowledged within 5 minutes')

    def test_allocate_not_enough_funds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))


        self.objects_wallet.create_new_transaction(transaction_name)
        self.objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 1)
        self.objects_wallet.add_output_to_transaction(transaction_name, self.second_address, 1)
        self.objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)

        self.assertTrue('Error totalling Outputs: Amount is out of range' in
                        self.objects_wallet.sign_transaction(transaction_name)['error']['data'])

    def test_list_transactions_api_call(self):
        self.assertTrue('transactions' in self.objects_wallet.list_all_transactions_in_factoid_blockchain(),
                        'Transactions are not listed')

    def test_list_transaction_by_id(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.objects_wallet.create_new_transaction(transaction_name)
        self.objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.objects_wallet.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.objects_wallet.sign_transaction(transaction_name)
        transaction = self.objects_wallet.compose_transaction(transaction_name)
        txid = self.objects_factomd.submit_factoid_by_transaction(transaction)['txid']
        wait_for_ack(txid)
        self.assertTrue(self.objects_wallet.list_transactions_by_txid(txid)['transactions'][0]['inputs'][0]['amount'] == 100000000, 'Transaction is not listed')

    def test_list_current_working_transactions_in_wallet(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.objects_wallet.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.objects_wallet.list_current_working_transactions_in_wallet())

    def test_delete_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.objects_wallet.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.objects_wallet.list_current_working_transactions_in_wallet())

        self.objects_wallet.delete_transaction(transaction_name)
        self.assertFalse(transaction_name in self.objects_wallet.list_current_working_transactions_in_wallet())

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.objects_wallet.create_new_transaction(transaction_name)
        self.objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.objects_wallet.add_entry_credit_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.objects_wallet.sign_transaction(transaction_name)
        transaction = self.objects_wallet.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.objects_factomd.submit_factoid_by_transaction(transaction)['message'])

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.objects_wallet.create_new_transaction(transaction_name)
        self.objects_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.objects_wallet.add_entry_credit_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.objects_wallet.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.objects_wallet.sign_transaction(transaction_name)
        transaction = self.objects_wallet.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.objects_factomd.submit_factoid_by_transaction(transaction)['message'])
        self.objects_factomd.get_pending_transactions()

    def create_chain_new(self, external_ids, content, ecpub):
        self.objects_wallet.compose_chain_new(self, external_ids, content, ecpub)

