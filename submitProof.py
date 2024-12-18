import eth_account
from eth_account import Account
import random
import string
import json
from pathlib import Path
from web3 import Web3
from web3.middleware import geth_poa_middleware  # Necessary for POA chains
from eth_account.messages import encode_defunct

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/23a76e550dbb464886b7b4d8b18816e4'))

def merkle_assignment():
    """
        The only modifications you need to make to this method are to assign
        your "random_leaf_index" and uncomment the last line when you are
        ready to attempt to claim a prime. You will need to complete the
        methods called by this method to generate the proof.
    """
    # Generate the list of primes as integers
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)

    # Create a version of the list of primes in bytes32 format
    leaves = convert_leaves(primes)

    # Build a Merkle tree using the bytes32 leaves as the Merkle tree's leaves
    tree = build_merkle(leaves)

    # Select a random leaf and create a proof for that leaf
    # Select an unclaimed random leaf and create a proof for that leaf
    random_leaf_index = random.randint(0, num_of_primes - 1)

    proof = prove_merkle(tree, random_leaf_index)

    # This is the same way the grader generates a challenge for sign_challenge()
    challenge = ''.join(random.choice(string.ascii_letters) for i in range(32))
    # Sign the challenge to prove to the grader you hold the account
    addr, sig = sign_challenge(challenge)

    if sign_challenge_verify(challenge, addr, sig):
        tx_hash = '0x'
        # TODO, when you are ready to attempt to claim a prime (and pay gas fees),
        # complete this method and run your code with the following line un-commented
        tx_hash = send_signed_msg(proof, leaves[random_leaf_index])

def is_leaf_claimed(leaf):
    """
    Checks if a specific prime (leaf) has already been claimed.
    Returns True if claimed, False otherwise.
    """
    owner = contract.functions.getOwnerByPrime(leaf).call()
    return owner != "0x0000000000000000000000000000000000000000"

def generate_primes(num_primes):
    """
        Function to generate the first 'num_primes' prime numbers
        returns list (with length n) of primes (as ints) in ascending order
    """
    primes_list = []

    #TODO YOUR CODE HERE
    candidate = 2

    while len(primes_list) < num_primes:
        #check if number is prime
        is_prime = True
        for prime in primes_list:
            if candidate % prime == 0:
                is_prime = False
                break
            
        # If candidate is prime, add to the list
        if is_prime:
            primes_list.append(candidate)

        candidate += 1

    return primes_list


def convert_leaves(primes_list):
    """
        Converts the leaves (primes_list) to bytes32 format
        returns list of primes where list entries are bytes32 encodings of primes_list entries
    """

    # TODO YOUR CODE HERE
    bytes32_primes = []
    for prime in primes_list:
        bytes32_primes.append(prime.to_bytes(32, byteorder='big'))

    return bytes32_primes


def build_merkle(leaves):
    """
        Function to build a Merkle Tree from the list of prime numbers in bytes32 format
        Returns the Merkle tree (tree) as a list where tree[0] is the list of leaves,
        tree[1] is the parent hashes, and so on until tree[n] which is the root hash
        the root hash produced by the "hash_pair" helper function
    """

    #TODO YOUR CODE HERE
    tree = []

    tree = [leaves]  # Start the tree with the leaves as the first layer

    while len(tree[-1]) > 1:
        layer = []
        current_layer = tree[-1]

        # Pairwise hash nodes in the current layer to form the next layer
        for i in range(0, len(current_layer), 2):
            left = current_layer[i]
            right = current_layer[i + 1] if i + 1 < len(current_layer) else current_layer[i]  # Duplicate if odd
            parent = hash_pair(left, right)
            layer.append(parent)
        
        tree.append(layer)  # Add the new layer to the tree

    return tree


def prove_merkle(merkle_tree, random_indx):
    """
        Takes a random_index to create a proof of inclusion for and a complete Merkle tree
        as a list of lists where index 0 is the list of leaves, index 1 is the list of
        parent hash values, up to index -1 which is the list of the root hash.
        returns a proof of inclusion as list of values
    """
    merkle_proof = []
    # TODO YOUR CODE HERE

    index = random_indx  # Start with the leaf index

    # Traverse each layer from the leaves up to the root
    for layer in merkle_tree[:-1]:  # Exclude the last layer (root hash layer)
        # Determine sibling index
        if index % 2 == 0:
            sibling_index = index + 1 if index + 1 < len(layer) else index  # Handle odd count case
        else:
            sibling_index = index - 1
        
        # Add the sibling hash to the proof
        merkle_proof.append(layer[sibling_index])
        
        # Move up to the next layer; each parent index is index // 2
        index //= 2

    return merkle_proof


def sign_challenge(challenge):
    """
        Takes a challenge (string)
        Returns address, sig
        where address is an ethereum address and sig is a signature (in hex)
        This method is to allow the auto-grader to verify that you have
        claimed a prime
    """
    acct = get_account()

    addr = acct.address
    eth_sk = acct.key

    # TODO YOUR CODE HERE
    message = encode_defunct(text=challenge)
    eth_sig_obj = w3.eth.account.sign_message(message,private_key=eth_sk)
    
    assert isinstance(eth_sig_obj, eth_account.datastructures.SignedMessage)

    return addr, eth_sig_obj.signature.hex()


def send_signed_msg(proof, random_leaf):
    """
        Takes a Merkle proof of a leaf, and that leaf (in bytes32 format)
        builds signs and sends a transaction claiming that leaf (prime)
        on the contract
    """
    chain = 'bsc'

    acct = get_account()
    address, abi = get_contract_info(chain)
    w3 = connect_to(chain)

    # TODO YOUR CODE HERE

    # Connect to the contract using the address and ABI
    contract = w3.eth.contract(address=address, abi=abi)

    # Build the transaction to call the contract's "submit" function
    # The "submit" function expects the proof as a list of bytes32 and the leaf as a single bytes32
    transaction = contract.functions.submit(proof, random_leaf).build_transaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 200000,  # Adjust gas limit if necessary
        'gasPrice': w3.eth.gas_price,
    })

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, acct.key)

    # Send the transaction and get the transaction hash
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()

    return tx_hash


# Helper functions that do not need to be modified
def connect_to(chain):
    """
        Takes a chain ('avax' or 'bsc') and returns a web3 instance
        connected to that chain.
    """
    if chain not in ['avax','bsc']:
        print(f"{chain} is not a valid option for 'connect_to()'")
        return None
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    else:
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    w3 = Web3(Web3.HTTPProvider(api_url))
    # inject the poa compatibility middleware to the innermost layer
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3


def get_account():
    """
        Returns an account object recovered from the secret key
        in "sk.txt"
    """
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath('sk.txt'), 'r') as f:
        sk = f.readline().rstrip()
    if sk[0:2] == "0x":
        sk = sk[2:]
    return eth_account.Account.from_key(sk)


def get_contract_info(chain):
    """
        Returns a contract address and contract abi from "contract_info.json"
        for the given chain
    """
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath("contract_info.json"), "r") as f:
        d = json.load(f)
        d = d[chain]
    return d['address'], d['abi']


def sign_challenge_verify(challenge, addr, sig):
    """
        Helper to verify signatures, verifies sign_challenge(challenge)
        the same way the grader will. No changes are needed for this method
    """
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)

    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == addr:
        print(f"Success: signed the challenge {challenge} using address {addr}!")
        return True
    else:
        print(f"Failure: The signature does not verify!")
        print(f"signature = {sig}\naddress = {addr}\nchallenge = {challenge}")
        return False


def hash_pair(a, b):
    """
        The OpenZeppelin Merkle Tree Validator we use sorts the leaves
        https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/MerkleProof.sol#L217
        So you must sort the leaves as well

        Also, hash functions like keccak are very sensitive to input encoding, so the solidity_keccak function is the function to use

        Another potential gotcha, if you have a prime number (as an int) bytes(prime) will *not* give you the byte representation of the integer prime
        Instead, you must call int.to_bytes(prime,'big').
    """
    if a < b:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [a, b])
    else:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [b, a])


if __name__ == "__main__":
    merkle_assignment()
