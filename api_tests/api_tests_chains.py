import unittest
import os, binascii

from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json
# from helpers.general_test_methods import wait_for_ack, wait_for_entry_in_block, fund_entry_credit_address
from nose.plugins.attrib import attr

@attr(api=True)
class APIEntriesTests(unittest.TestCase):

    def setUp(self):
        self.factom_api = APIObjectsFactomd()
        self.wallet_api_objects = APIObjectsWallet()
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def test_commit_chain(self):
        # commit chain
        message, external_ids = self.__compose_chain()
        commit_success, commit_response = self.factom_api.commit_chain_by_message(message)
        self.factom_api.get_pending_entries()
        if not commit_success:
            fail_message, info, entryhash = self.__failure_data(commit_response)
            self.assertTrue(False, 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)

    def test_repeated_commits(self):
        balance_before = self.factom_api.get_entry_credits_balance_by_ec_address(self.entry_credit_address1000)

        # commit chain
        message, external_ids = self.__compose_chain()
        commit_success, commit_response = self.factom_api.commit_chain_by_message(message)

        if not commit_success:
            fail_message, info, entryhash = self.__failure_data(commit_response)
            self.assertNotIn('Repeated Commit', fail_message,
                             'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)
            # failed for some other reason
            self.assertTrue(False, 'Chain commit failed - ' + fail_message)
        else:
            # wait for 1st commit to be acknowledged
            tx_id = commit_response['txid']
            wait_for_ack(tx_id)

        # try to repeat commit
        commit_success, commit_response = self.factom_api.commit_chain_by_message(message)

        if commit_success:
            self.assertFalse(True, 'Repeated commit allowed - entryhash ' + str(commit_response['entryhash']))
        else:
            fail_message, info, entryhash = self.__failure_data(commit_response)
            self.assertIn('Repeated Commit', fail_message, 'Chain commit failed because of - ' + fail_message + ' - ' + info + ' instead of Repeated Commit - entryhash ' + entryhash)

        # see if 2nd commit has been mistakenly paid for
        wait_for_entry_in_block(external_id_list=external_ids)
        balance_after = self.factom_api.get_entry_credits_balance_by_ec_address(self.entry_credit_address1000)
        self.assertEqual(balance_before, balance_after + 12, 'Balance before commit = ' + str(balance_before) + '. Balance after commit = ' + str(balance_after) + '. Balance after single commit SHOULD be = ' + str(balance_after + 12))

    def __compose_chain(self):

        # external ids must be in hex
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        external_ids = [name_1, name_2]

        # content must be in hex
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        with open(path, 'r') as fin:
            content = binascii.hexlify(fin.read())

        # compose chain
        message, entry = self.wallet_api_objects.compose_chain(external_ids, content, self.entry_credit_address1000)

        return message, external_ids

    def __failure_data(self, commit_response):
        message = str(commit_response['message'])
        info = str(commit_response['data']['info'])
        entryhash = str(commit_response['data']['entryhash'])
        return message, info, entryhash
