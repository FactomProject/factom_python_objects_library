import unittest, time

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers import read_data_from_json

cli_create = CLIObjectsCreate()
chain_objects = CLIObjectsChain()
data = read_data_from_json('shared_test_data.json')

ACK_WAIT_TIME = 20
BLOCK_WAIT_TIME = 50

def wait_for_ack(transaction_id):
    for x in range(0, BLOCK_WAIT_TIME):
        if 'TransactionACK' in cli_create.request_transaction_acknowledgement(transaction_id):
            break
        time.sleep(1)

def wait_for_entry_in_block(**kwargs):
    chain_identifier = ''
    if 'external_id_list' in kwargs:
        chain_identifier = ' '.join(kwargs['external_id_list'])
    for x in range(0, BLOCK_WAIT_TIME):
        if 'Chain not yet included in a Directory Block' not in chain_objects.get_chainhead(external_id_list=[chain_identifier]):
            break
        time.sleep(1)

def fund_entry_credit_address(amount):
    # all entry credit addresses are funded from first_address
    first_address = cli_create.import_addresses(data['factoid_wallet_address'])[0]
    entry_credit_address = cli_create.create_entry_credit_address()
    text = cli_create.buy_entry_credits(first_address, entry_credit_address, str(amount))
    chain_dict = chain_objects.parse_simple_data(text)
    tx_id = chain_dict['TxID']
    wait_for_ack(tx_id)
    return entry_credit_address