import csv
from web3 import Web3

# Avalanche Testnet RPC URL
AVALANCHE_TESTNET_RPC = "https://api.avax-test.network/ext/bc/C/rpc"
BNB_TESTNET_RPC = "https://data-seed-prebsc-1-s1.binance.org:8545/"

# Private key and source contract address
PRIVATE_KEY = "0x5d7d0513d25b385d466ea87ebe0b7c2f69b2300bc32dfe70742db5137f104af9"
SOURCE_CONTRACT_ADDRESS = "0xB0b0bC6E19Cd307D843Bb1F5217Ddd8685752629"
DESTINATION_CONTRACT_ADDRESS = "0xBA2909dC5C03342185bE6110dDDeABAdbFBa7Ca4"

SOURCE_CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "_token", "type": "address"}],
        "name": "registerToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]
DESTINATION_CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "_underlying_token", "type": "address"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "symbol", "type": "string"},
        ],
        "name": "createToken",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

# Initialize Web3 instance
web3 = Web3(Web3.HTTPProvider(AVALANCHE_TESTNET_RPC))
assert web3.isConnected(), "Failed to connect to Avalanche Testnet"

# Initialize Web3 instances
avalanche_web3 = Web3(Web3.HTTPProvider(AVALANCHE_TESTNET_RPC))
bnb_web3 = Web3(Web3.HTTPProvider(BNB_TESTNET_RPC))

assert avalanche_web3.isConnected(), "Failed to connect to Avalanche Testnet"
assert bnb_web3.isConnected(), "Failed to connect to BNB Testnet"

# Initialize contracts
source_contract = avalanche_web3.eth.contract(
    address=Web3.to_checksum_address(SOURCE_CONTRACT_ADDRESS),
    abi=SOURCE_CONTRACT_ABI,
)
destination_contract = bnb_web3.eth.contract(
    address=Web3.to_checksum_address(DESTINATION_CONTRACT_ADDRESS),
    abi=DESTINATION_CONTRACT_ABI,
)

# Get wallet address 
wallet_address = web3.eth.account.from_key(PRIVATE_KEY).address

# Function to send a transaction
def send_register_token_transaction(token_address):
    # Get the nonce
    nonce = web3.eth.get_transaction_count(wallet_address)
    # Build the transaction
    transaction = source_contract.functions.registerToken(
        Web3.to_checksum_address(token_address)
    ).build_transaction({
        "chainId": web3.eth.chain_id,
        "gas": 2000000,
        "gasPrice": web3.to_wei("20", "gwei"),
        "nonce": nonce,
    })
    # Sign the transaction
    signed_tx = web3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
    # Send the transaction and get the hash
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    return tx_hash

# Function to send a transaction for createToken on Destination
def send_create_token_transaction(token_address, name, symbol):
    nonce = bnb_web3.eth.get_transaction_count(wallet_address)
    transaction = destination_contract.functions.createToken(
        Web3.to_checksum_address(token_address),
        name,
        symbol,
    ).build_transaction({
        "chainId": bnb_web3.eth.chain_id,
        "gas": 3000000,
        "gasPrice": bnb_web3.to_wei("20", "gwei"),
        "nonce": nonce,
    })
    signed_tx = bnb_web3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
    tx_hash = bnb_web3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    return tx_hash

# Main function to process tokens
def main():
    # List of tokens to process along with their names and symbols
    tokens = [
        {
            "address": "0xc677c31AD31F73A5290f5ef067F8CEF8d301e45c",
            "name": "TokenA",
            "symbol": "TKNA",
        },
        {
            "address": "0x0773b81e0524447784CcE1F3808fed6AaA156eC8",
            "name": "TokenB",
            "symbol": "TKNB",
        },
    ]

    for token in tokens:
        token_address = token["address"]
        name = token["name"]
        symbol = token["symbol"]

        print(f"Processing token: {token_address} (Name: {name}, Symbol: {symbol})")

        # Register token on Source (Avalanche)
        print(f"Registering token on Source contract: {token_address}")
        register_tx_hash = send_register_token_transaction(token_address)
        print(f"Source registration transaction hash: {register_tx_hash}")

        # Create token on Destination (BNB)
        print(f"Creating token on Destination contract: {token_address}")
        create_tx_hash = send_create_token_transaction(token_address, name, symbol)
        print(f"Destination creation transaction hash: {create_tx_hash}")

    print("All tokens processed successfully.")

if __name__ == "__main__":
    main()
