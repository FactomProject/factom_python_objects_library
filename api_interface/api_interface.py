import ast, json, random, requests, string, time

class APIInterface():
    '''
    Needs to be initialized with (including ports)
    - a valid factomd_address, and
    - a valid wallet_address
    '''
    def __init__(self, factomd_address, wallet_address):
        self.factomd_address = factomd_address
        self.wallet_address = wallet_address
    '''
    For all three 'send requests' below:
    :param destination: str, if 'wallet' then the API call will be sent to the factom-walletd port (8089)
                             else the API call will be sent to the factomd port (8088)
    :param method: str, name of the API method to call
    :param params_dict: dictionary, the parameters to be sent with the API call
    :return: result of the API call
    '''
    def send_post_request_with_params_dict(self, destination, method, params_dict):
        address = "10.41.0.215:8089" if destination == 'wallet' else "10.41.0.5:8088"
        url = 'http://'+ address +'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        print data
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def send_get_request_with_params_dict(self, destination, method, params_dict):
        address = "10.41.0.215:8089" if destination == 'wallet' else "10.41.0.5:8088"
        url = 'http://' + address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

    def send_get_request_with_method(self, destination, method):
        address = "10.41.0.215:8089" if destination == 'wallet' else "10.41.0.5:8088"
        url = 'http://' + address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text
# --------------------------------------------------------------------------------------------------

    def get_all_addresses(self):
        '''
        Return all addresses in wallet
        :return return_data: list, JSON pairs of addresses known to the wallet
            secret
            public
        :return error_message: str, nil for no error
        '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "method": 'all-addresses'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.get(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']['addresses']
            error_message = ''
        return return_data, error_message

    def import_addresses(self, *secret_addresses):
        '''
        Bring already existing addresses into the wallet
        :param *secret_addresses: unlimited number of str, private keys of all the external factoid and                                      entry credit addresses to be imported
        :return return_data: list, the public keys corresponding to the input addresses, in the same order
        :return error_message: str, nil for no error
        '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'addresses': [{'secret': address} for address in secret_addresses]})), "method": 'import-addresses'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = []
            print 'result', block['result']
            for i in range(len(secret_addresses)):
                return_data.append(block['result']['addresses'][i]['public'])
            print "return_data", return_data
            error_message = ''
        return return_data, error_message

    def generate_entry_credit_address(self):
        '''
        Generate a new entry credit address
        :return public: str, public key of the newly generated entry credit address
        :return secret: str, private key of the newly generated entry credit address
        :return error_message: str, nil for no error
        '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "method": 'generate-ec-address'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.get(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            public = ''
            secret = ''
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            public = block['result']['public']
            secret = block['result']['secret']
            error_message = ''
        return public, secret, error_message

    def generate_factoid_address(self):
        '''
        :return public: str, public key of the newly generated factoid address
        :return secret: str, private key of the newly generated factoid address
        :return error_message: str, nil for no error
        '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "method": 'generate-factoid-address'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.get(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            public = ''
            secret = ''
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            public = block['result']['public']
            secret = block['result']['secret']
            error_message = ''
        return public, secret, error_message
# --------------------------------------------------------------------------------------------------

    def create_chain(self, external_ids, content, ec_address):
        '''
        Create a new chain
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
        :param content: str, the content (in hex) of the 1st entry of the chain
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
        :return txid: str
        :return entryhash: str
        :return chainid: str
        :return error_message: str, nil for no error
        '''
        txid = ''
        entryhash = ''
        chainid = ''
        compose, error_message = self.compose_chain(external_ids, content, ec_address)
        print 'compose', compose
        if not error_message:
            commit, error_message = self.commit_chain(compose['commit']['params']['message'])
            print 'commit', commit
            if not error_message:
                reveal, error_message = self.reveal_chain(compose['reveal']['params']['entry'])
                print 'reveal', reveal
                if not error_message:
                    txid = commit['txid']
                    entryhash = commit['entryhash']
                    chainid = reveal['chainid']
        return txid, entryhash, chainid, error_message

    def compose_chain(self, external_ids, content, ec_address):
        '''
        Create both the 'commit-chain' JSON and the 'reveal-chain' JSON that can then be sent in API calls to create a chain at a later time
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
        :param content: str, the content (in hex) of the 1st entry of the chain
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
        :return return_data: if API call succeeds, JSON of the two API calls (commit and reveal) that when sent later will actually create the chain
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
       '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'chain': {'firstentry': {'extids': external_ids, 'content': content}}, 'ecpub': ec_address})), "method": 'compose-chain'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def commit_chain(self, message):
        '''
        Commit chain by message
        :param message: str, the message portion of the API call
        :return return_data: if API call succeeds, transaction JSON block containing:
            message:"Chain Commit Success"
            txid
            entryhash
            chainidhash
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'message': message})), "method": 'commit-chain'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def reveal_chain(self, entry):
        '''
        Reveal chain by entry
        :param entry: str, the entry portion of the API call
        :return: return_data: if API call succeeds, reveal JSON block containing:
            message":"Entry Reveal Success"
            entryhash
            chainid
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
      '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'entry': entry})), "method": 'reveal-chain'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message
# --------------------------------------------------------------------------------------------------

    def create_entry(self, chain_id, external_ids, content, ec_address):
        '''
        Create a new entry in an existing chain
        :param chain_id: str, chain ID of existing chain in which to put the entry
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the entry
        :param content: str, the content (in hex) of the entry
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the entry
        :return txid: str
        :return entryhash: str
        :return chainid: str
        :return error_message: str, nil for no error
        '''
        txid = ''
        entryhash = ''
        chainid = ''
        compose, error_message = self.compose_entry(chain_id, external_ids, content, ec_address)
        print 'compose', compose
        if not error_message:
            compose_message = compose['commit']['params']['message']
            compose_entry = compose['reveal']['params']['entry']
            commit, error_message = self.commit_entry(compose['commit']['params']['message'])
            print 'commit', commit
            if not error_message:
                print 'txid', commit['txid']
                print 'entryhash', commit['entryhash']

                # no wait necessary between commit and reveal

                #  ack commit c with txid
                for x in range(0, 40):
                    status = self.get_transaction_status(commit['txid'], 'c')
                #     status = self.get_transaction_status('', 'c', compose_message)
                    if any(accepted in str(status) for accepted in ('TransactionACK', 'DBlockConfirmed')): break
                    time.sleep(1)

                # check ack commit c with txid after 10 minutes
                # time.sleep(600)
                # self.get_transaction_status(commit['txid'], 'c')

                reveal, error_message = self.reveal_entry(compose['reveal']['params']['entry'])
                print 'reveal', reveal
                if not error_message:

                    # ack reveal
                    for x in range(0, 40):
                        status = self.get_transaction_status(commit['entryhash'], 'f')
                        # status = self.get_transaction_status(commit['entryhash'], reveal['chainid'])
                        # status = self.get_transaction_status('', reveal['chainid'], compose_entry)
                        # status = self.get_transaction_status('', 'f', compose_entry)
                        # status = self.get_transaction_status(commit['txid'], reveal['chainid'])
                        if any(accepted in str(status) for accepted in ('TransactionACK', 'DBlockConfirmed')): break
                        time.sleep(1)

                    txid = commit['txid']
                    entryhash = commit['entryhash']
                    chainid = reveal['chainid']

                    # for x in range(0, 140):
                    #     status = self.get_transaction_status(commit['txid'], 'c')
                    #     if any(accepted in str(status) for accepted in ('TransactionACK', 'DBlockConfirmed')): break
                    #     time.sleep(1)

        return txid, entryhash, chainid, error_message

    def compose_entry(self, chain_id, external_ids, content, ec_address):
        '''
        Create both the 'commit-entry' JSON and the 'reveal-entry' JSON that can then be sent in API calls to create an entry at a later time
         :param chain_id: str, chain ID of existing chain in which to put the entry
         :param external_ids: list, all the external ids (in hex) that will determine the identity of the entry
         :param content: str, the content (in hex) of the entry
         :param ec_address: str, the public key of the entry credit address that will pay for the creation of the entry
        :return return_data: if API call succeeds, JSON of the two API calls (commit and reveal) that when sent later will actually create the entry
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
       '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'entry': {'chainid':chain_id, 'extids': external_ids, 'content': content}, 'ecpub': ec_address})), "method": 'compose-entry'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def commit_entry(self, message):
        '''
        Commit entry by message
        :param message: str, the message portion of the API call
        :return block['error']: if API call failed, the contents of the 'error' JSON block
        :return block['result']: if API call succeeded, the contents of the 'result' JSON block
        :return return_data: if API call succeeds, transaction JSON block containing:
            message:"Chain Commit Success".
            txid
            entryhash
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
       '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'message': message})), "method": 'commit-entry'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def reveal_entry(self, entry):
        '''
        Reveal chain by entry
        :param entry: str, the entry portion of the API call
        :return return_data: if API call succeeds, reveal JSON block containing:
            message":"Entry Reveal Success"
            entryhash
            chainid
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
       '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'entry': entry})), "method": 'reveal-entry'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message
# --------------------------------------------------------------------------------------------------

    def send_factoids(self, from_address, to_address, factoids):
        '''
        Move factoids from one factoid address to another
        :param from_address: str, source factoid address of the factoids
        :param to_address: str, destination factoid address of the factoids
        :param factoids: int, amount of factoids to transfer
        :return return_data: if API call succeeds, str, txid
        if API call fails, error JSON block containing:
          code
          message
          data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        factoshis = int(factoids * 1e8)
        return_data = ''
        error_message = self.create_new_transaction(transaction_name)[1]
        if not error_message:
            error_message = self.add_input_to_transaction(transaction_name, from_address, factoshis)[1]
            if not error_message:
                error_message = self.add_output_to_transaction(transaction_name, to_address, factoshis)[1]
                if not error_message:
                    error_message = self.subtract_fee_from_transaction(transaction_name, to_address)[1]
                    if not error_message:
                        error_message = self.sign_transaction(transaction_name)[1]
                        if not error_message:
                            transaction, error_message = self.compose_transaction(transaction_name)
                            if not error_message:
                                result, error_message = self.submit_factoid_transaction(transaction)
                                if error_message: return_data = ''
                                else: return_data = result['txid']
        return return_data, error_message

    def buy_entry_credits(self, from_address, to_address, entry_credits):
        '''
        Convert factoids into entry credits
        :param from_address: str, source factoid address of the factoids
        :param to_address: str, destination entry credit address of the entry credits
        :param entry_credits: int, amount of entry credits to arrive at the entry credit address
        :return return_data: if API call succeeds, str, txid
        if API call fails, error JSON block containing:
          code
          message
          data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        ecrate = self.get_entry_credit_rate()[0]
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        entry_credit_factoshis = entry_credits * ecrate
        return_data = ''
        error_message = self.create_new_transaction(transaction_name)[1]
        if not error_message:
            error_message = self.add_input_to_transaction(transaction_name, from_address, entry_credit_factoshis)[1]
            if not error_message:
                error_message = self.add_entry_credit_output_to_transaction(transaction_name, to_address, entry_credit_factoshis)[1]
                if not error_message:
                    error_message = self.add_fee_to_transaction(transaction_name, from_address)[1]
                    if not error_message:
                        error_message = self.sign_transaction(transaction_name)[1]
                        if not error_message:
                            transaction, error_message = self.compose_transaction(transaction_name)
                            if not error_message:
                                result, error_message = self.submit_factoid_transaction(transaction)
                                if error_message: return_data = ''
                                else: return_data = result['txid']
        return return_data, error_message

    def create_new_transaction(self, transaction_name):
        '''
        Create new transaction
        :param transaction_name: str, name of the transaction
        :return return_data: if API call succeeds, transaction JSON block containing:
            feesrequired
            signed
            name
            timestamp
            totalecoutputs
            totalinputs
            totaloutputs
            inputs
                address
                amount
            outputs
                address
                amount
            ecoutputs
                address
                amount
            txid
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name})), "method": 'new-transaction'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def add_input_to_transaction(self, transaction_name, address, amount):
        '''
        Add input to transaction
        :param transaction_name: str, name of the transaction
        :param address: str, source of the factoid input
        :param amount: int, amount of the input in factoshis (factoids * 1e8)
        :return return_data: if API call succeeds, transaction JSON block containing:
            feespaid
            feesrequired
            signed
            name
            timestamp
            totalecoutputs
            totalinputs
            totaloutputs
            inputs
                address
                amount
            outputs
                address
                amount
            ecoutputs
                address
                amount
            txid
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name, 'address':address,'amount': amount})), "method": 'add-input'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def add_output_to_transaction(self, transaction_name, address, amount):
        '''
         Add output to transaction
         :param transaction_name: str, name of the transaction
         :param address: str, destination of the factoid output
         :param amount: int, amount of the output in factoshis (factoids * 1e8)
         :return return_data: if API call succeeds, transaction JSON block containing:
             feespaid
             feesrequired
             signed
             name
             timestamp
             totalecoutputs
             totalinputs
             totaloutputs
             inputs
                 address
                 amount
             outputs
                 address
                 amount
             ecoutputs
                 address
                 amount
             txid
         if API call fails, error JSON block containing:
             code
             message
             data (optional)
         :return error_message: if API call succeeds, nil
         if API call fails, useful error message
         '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name, 'address':address,'amount': amount})), "method": 'add-output'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def add_entry_credit_output_to_transaction(self, transaction_name, address, amount):
        '''
         Add entry credit output to transaction
         :param transaction_name: str, name of the transaction
         :param address: str, destination of the entry credit output
         :param amount: int, amount of the entry credit output in factoshis (factoids * 1e8)
         :return return_data: if API call succeeds, transaction JSON block containing:
             feespaid
             feesrequired
             signed
             name
             timestamp
             totalecoutputs
             totalinputs
             totaloutputs
             inputs
                 address
                 amount
             outputs
                 address
                 amount
             ecoutputs
                 address
                 amount
             txid
         if API call fails, error JSON block containing:
             code
             message
             data (optional)
         :return error_message: if API call succeeds, nil
         if API call fails, useful error message
         '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name, 'address':address,'amount': amount})), "method": 'add-ec-output'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def add_fee_to_transaction(self, transaction_name, address):
        '''
         Add fee onto one of the inputs to a transaction
         :param transaction_name: str, name of the transaction
         :param address: str, source address from which to increase the input in order to cover the needed fee
         :return return_data: if API call succeeds, transaction JSON block containing:
             feespaid
             feesrequired
             signed
             name
             timestamp
             totalecoutputs
             totalinputs
             totaloutputs
             inputs
                 address
                 amount
             outputs
                 address
                 amount
             ecoutputs
                 address
                 amount
             txid
         if API call fails, error JSON block containing:
             code
             message
             data (optional)
         :return error_message: if API call succeeds, nil
         if API call fails, useful error message
         '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name, 'address': address})), "method": 'add-fee'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def subtract_fee_from_transaction(self, transaction_name, address):
        '''
         Subtract fee from one of the outputs of a transaction
         :param transaction_name: str, name of the transaction
         :param address: str, destination address from which to subtract the needed fee
         :return return_data: if API call succeeds, transaction JSON block containing:
             feespaid
             feesrequired
             signed
             name
             timestamp
             totalecoutputs
             totalinputs
             totaloutputs
             inputs
                 address
                 amount
             outputs
                 address
                 amount
             ecoutputs
                 address
                 amount
             txid
         if API call fails, error JSON block containing:
             code
             message
             data (optional)
         :return error_message: if API call succeeds, nil
         if API call fails, useful error message
         '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name, 'address': address})), "method": 'sub-fee'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def sign_transaction(self, transaction_name):
        '''
          Attach signatures of (data + each input private key) to a transaction
          :param transaction_name: str, name of the transaction
          :return return_data: if API call succeeds, transaction JSON block containing:
              feespaid
              feesrequired
              signed
              name
              timestamp
              totalecoutputs
              totalinputs
              totaloutputs
              inputs
                  address
                  amount
              outputs
                  address
                  amount
              ecoutputs
                  address
                  amount
              txid
          if API call fails, error JSON block containing:
              code
              message
              data (optional)
          :return error_message: if API call succeeds, nil
          if API call fails, useful error message
          '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name})), "method": 'sign-transaction'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def compose_transaction(self, transaction_name):
        '''
        Create the message that can then be sent in a 'factoid-submit' API call to create an entire transaction at a later time
        :param transaction_name: str, name of the transaction
        :return return_data: if API call succeeds, message that can then be sent in a 'factoid-submit' API call to create an entire transaction at a later time
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
       '''
        url = 'http://' + self.wallet_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'tx-name': transaction_name})), "method": 'compose-transaction'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block["result"]['params']['transaction']
            error_message = ''
        return return_data, error_message

    def submit_factoid_transaction(self, transaction):
        '''
        Submit previously composed transaction
        :param transaction: str, full transaction hash of previously composed transaction
        :return return_data: if API call succeeds, transaction JSON block containing:
          message":"Successfully submitted the transaction"
          txid
        if API call fails, error JSON block containing:
          code
          message
          data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'transaction':
 transaction})), "method": 'factoid-submit'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def get_transaction_status(self, hash_or_tx_id, chain_id, fulltransaction=''):
        '''
        This api call is used to find the status of a transaction, whether it be a factoid, commit entry, or reveal entry. It has been inappropriately overloaded.
        :param hash_or_tx_id: str,
               tx_id is meant for use with a commit entry or factoid transaction
               entry hash is meant for use with a reveal entry
               fulltransaction SHOULD have been folded in here, but wasn't
        :param chain_id: str,
               chain_id for factoid transaction is always 000...f, abbreviated to just f
               chain_id for commit entry is always 000...c, abbreviated to just c
               chain_id for reveal entry is actual chain_id
        :param fulltransaction: str, full marshaled transaction may be given instead of entry hash, and the                entry hash will be derived from it

        for factoid transaction:
        :return txid: str, transaction id
        :return transactiondate: Unix epoch time, timestamp of transaction, e.g. 1441138021975
        :return transactiondatestring: str, timestamp of transaction, e.g. 2015-09-01 15:07:01
        :return blockdate: Unix epoch time, timestamp of containing block, e.g. 1441137600000
        :return blockdatestring: str, timestamp of transaction, e.g. 2015-09-01 15:00:00
        :return status: str, status of the transaction (see status types below)

        for commit entry or reveal entry:
        :return committxid: str, transaction id
        :return entryhash: str, entry hash (for reveal entry only)
        :return commitdata_status: str, status of the committed entry (see status types below)
        :return entrydata_status: str, status of the revealed entry (see status types below) (for reveal                    entry only)

        status types:
        Unknown : not found anywhere
        NotConfirmed : found on local node, but not in network (holding map)
        TransactionACK : found in network, but not written to the blockchain yet (processList)
        DBlockConfirmed : found in blockchain
        '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'hash': hash_or_tx_id, 'chainid': chain_id, 'fulltransaction': fulltransaction})), "method": 'ack'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message
# --------------------------------------------------------------------------------------------------

    def get_pending_entries(self):
        '''
        Get all pending entries
        Note: an entry may not show as pending immediately after creation. Some wait time may be necessary.
        :return return_data: if API call succeeds, entry JSON block containing:
            EntryHash
            ChainID
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "method": 'pending-entries'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.get(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message
# --------------------------------------------------------------------------------------------------

    def get_pending_transactions(self):
        '''
        Get all pending transactions
        Note: a transaction may not show as pending immediately after creation. Some wait time may be necessary.
        :return return_data: if API call succeeds, transaction JSON block containing:
            for each transaction:
                TransactionID
                Status
                Inputs
                Outputs
                ECOutputs
                Fees
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "method": 'pending-transactions'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.get(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def get_entry_credit_rate(self):
        '''
        Get entry credit rate
        :return return_data: if API call succeeds, int, current number of entry credits to which 1 factoid can be converted
            if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "method": 'entry-credit-rate'}
        headers = {'content-type': 'text/plain'}
        print data
        block = json.loads(requests.get(url, data=json.dumps(data), headers=headers).text)
        block = json.loads(self.send_get_request_with_method('factomd', 'entry-credit-rate'))
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            print 'result', block['result']
            return_data = block['result']['rate']
            error_message = ''
        return return_data, error_message

    def get_entry_credit_balance(self, ec_address):
        '''
        Get entry credit balance by ec address
        :param ec_address: str, ec address
        :return return_data: if API call succeeds, int, entry credit address balance in entry credits
            if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
                if API call fails, useful error message
   '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'address': ec_address})), "method": 'entry-credit-balance'}
        headers = {'content-type': 'text/plain'}
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']['balance']
            error_message = ''
        return return_data, error_message

    def get_all_entry_credit_balances(self):
        '''
        List all entry credit addresses with their respective balances
        :return address_list: if API call succeeds, list of tuples
            entry credit address: str
            balance: int, in entry credits
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
   '''
        address_list = []
        all_addresses, error_message = self.get_all_addresses()
        if not error_message:
            for address in all_addresses:
                if address['public'][0] == 'E':
                    balance, error_message = self.get_entry_credit_balance(address['public'])
                    if not error_message:
                        address_list.append((address['public'], balance))
        return address_list, error_message

    def get_factoid_balance(self, factoid_address):
        '''
        Get factoid balance by factoid address
        :param factoid_address: str address
        :return return_data: if API call succeeds, int, factoid address balance in fatoshis (factoids * 10e-8)
            if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        url = 'http://' + self.factomd_address + '/v2'
        data = {"jsonrpc": "2.0", "id": 0, "params": ast.literal_eval(json.dumps({'address': factoid_address})), "method": 'factoid-balance'}
        headers = {'content-type': 'text/plain'}
        block = json.loads(requests.post(url, data=json.dumps(data), headers=headers).text)
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']['balance']
            error_message = ''
        return return_data, error_message

    def get_all_factoid_balances(self):
        '''
        List all factoid addresses with their respective balances
        :return address_list: if API call succeeds, list of tuples
            factoid address: str
            balance: int, in entry credits
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
   '''
        address_list = []
        all_addresses, error_message = self.get_all_addresses()
        if not error_message:
            for address in all_addresses:
                if address['public'][0] == 'F':
                    balance, error_message = self.get_factoid_balance(address['public'])
                    if not error_message:
                        address_list.append((address['public'], balance))
        return address_list, error_message

