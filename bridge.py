from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import json
import sys
from pathlib import Path

source_chain = 'avax'
destination_chain = 'bsc'
contract_info = "contract_info.json"

def connectTo(chain):
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['avax','bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

def getContractInfo(chain):
    """
        Load the contract_info file into a dictinary
        This function is used by the autograder and will likely be useful to you
    """
    p = Path(__file__).with_name(contract_info)
    try:
        with p.open('r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( "Failed to read contract info" )
        print( "Please contact your instructor" )
        print( e )
        sys.exit(1)

    return contracts[chain]

def scanBlocks(chain):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return

        #YOUR CODE HERE

		if chain == 'source':
				chain_name = source_chain

		elif chain == 'destination'
				chain_name = destination_chain

    # Load the contract info for both source and destination chains
    contract_info = getContractInfo(chain_name)
    w3 = connectTo(chain)
    
    # Get the contract ABI and address from the contract info
    contract_abi = contract_info['abi']
    contract_address = Web3.to_check_sum_address(contract_info['address'])
    
    # Get the contract instance
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Determine which event to scan for based on the chain
    if chain == 'source':
        # Listening for 'Deposit' event on the source chain
        event_signature = 'Deposit(address,address,uint256)'
    elif chain == 'destination':
        # Listening for 'Unwrap' event on the destination chain
        event_signature = 'Unwrap(address,address,address,address,uint256)'

    # Get the current block number
    latest_block = w3.eth.block_number
    
    # Loop through the last 5 blocks and scan for events
    for block_number in range(latest_block - 4, latest_block + 1):
        print(f"Scanning block {block_number}...")
        
        # Create an event filter for the specified block range
        event_filter = contract.events[event_signature].create_filter(fromBlock=block_number, toBlock=block_number)
        
        # Get events from the block
        new_entries = event_filter.get_all_entries()
        
        if not new_entries:
            print(f"No events found in block {block_number}.")
            continue
        
        for event in new_entries:
            print(f"Event detected: {event_signature}")
            
            if chain == 'source' and event.event == "Deposit":
                # If Deposit event is detected, call the 'wrap' function on destination contract
                token_address = event.args['token']
                recipient = event.args['recipient']
                amount = event.args['amount']
                
                # Call the wrap function on the destination contract
                destination_chain = 'bsc'  
                destination_contract_info = getContractInfo(destination_chain)
                destination_w3 = connectTo(destination_chain)
                
                # Get the destination contract ABI and address
                destination_contract_abi = destination_contract_info['abi']
                destination_contract_address = Web3.toChecksumAddress(destination_contract_info['address'])
                destination_contract = destination_w3.eth.contract(address=destination_contract_address, abi=destination_contract_abi)
                
                # Build the transaction for the wrap function
                wrap_tx = destination_contract.functions.wrap(token_address, recipient, amount).build_transaction({
                    'chainId': destination_w3.eth.chain_id,
                    'gas': 2000000,
                    'gasPrice': destination_w3.toWei("20", 'gwei'),
                    'nonce': destination_w3.eth.get_transaction_count(destination_contract_address)
                })
                
                # Sign the transaction
                signed_tx = destination_w3.eth.account.sign_transaction(wrap_tx, private_key='0x5d7d0513d25b385d466ea87ebe0b7c2f69b2300bc32dfe70742db5137f104af9') 
                tx_hash = destination_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"Wrap transaction sent on destination chain. Tx Hash: {destination_w3.toHex(tx_hash)}")

            elif chain == 'destination' and event.event == "Unwrap":
                # If Unwrap event is detected, call the 'withdraw' function on source contract
                token_address = event.args['underlying_token']
                recipient = event.args['to']
                amount = event.args['amount']
                
                # Call the withdraw function on the source contract
                source_chain = 'avax'  
                source_contract_info = getContractInfo(source_chain)
                source_w3 = connectTo(source_chain)
                
                # Get the source contract ABI and address
                source_contract_abi = source_contract_info['abi']
                source_contract_address = Web3.toChecksumAddress(source_contract_info['address'])
                source_contract = source_w3.eth.contract(address=source_contract_address, abi=source_contract_abi)
                
                # Build the transaction for the withdraw function
                withdraw_tx = source_contract.functions.withdraw(token_address, recipient, amount).build_transaction({
                    'chainId': source_w3.eth.chain_id,
                    'gas': 2000000,
                    'gasPrice': source_w3.toWei("20", 'gwei'),
                    'nonce': source_w3.eth.get_transaction_count(source_contract_address)
                })
                
                # Sign the transaction
                signed_tx = source_w3.eth.account.sign_transaction(withdraw_tx, private_key='0x5d7d0513d25b385d466ea87ebe0b7c2f69b2300bc32dfe70742db5137f104af9') 
                tx_hash = source_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"Withdraw transaction sent on source chain. Tx Hash: {source_w3.toHex(tx_hash)}")

    print(f"Finished scanning the last 5 blocks on the {chain} chain.")
