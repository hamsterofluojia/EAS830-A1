from web3 import Web3
import eth_account
import os

def get_keys(challenge,keyId = 0, filename = "eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """

    w3 = Web3()

    msg = eth_account.messages.encode_defunct(challenge)

	#YOUR CODE HERE
    # Load existing private keys from the file, if any
    mnemonics = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            mnemonics = [line.strip() for line in f if line.strip()]

    # Generate and save a new private key if needed for the specified keyId
    if keyId >= len(mnemonics):
        new_account = w3.eth.account.create()  # Generate a new account
        private_key_hex = new_account.privateKey.hex()  # Get the private key in hex format
        mnemonics.append(new_private_key)
        
        # Write all private keys to the file
        with open(filename, "w") as f:
            f.write("\n".join(mnemonics))
        
        # Use the new account for signing
        eth_addr = new_account.address
    else:
        # If using an existing key, retrieve it and create the account
        private_key_hex = mnemonics[keyId]
        existing_account = w3.eth.account.from_key(private_key_hex)  # Create the account from the stored private key
        eth_addr = existing_account.address

    # Sign the challenge message
    sig = w3.eth.account.sign_message(msg, private_key=private_key_hex)

    assert eth_account.Account.recover_message(msg,signature=sig.signature.hex()) == eth_addr, f"Failed to sign message properly"

    #return sig, acct #acct contains the private key
    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr= get_keys(challenge=challenge,keyId=i)
        print( addr )
