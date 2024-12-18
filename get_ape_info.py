from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

#You will need the ABI to connect to the contract
#The file 'abi.json' has the ABI for the bored ape contract
#In general, you can get contract ABIs from etherscan
#https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
	abi = json.load(f) 

############################
#Connect to an Ethereum node
api_url = 'https://mainnet.infura.io/v3/23a76e550dbb464886b7b4d8b18816e4' #YOU WILL NEED TO TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_ape_info(apeID):
	assert isinstance(apeID,int), f"{apeID} is not an int"
	assert 1 <= apeID, f"{apeID} must be at least 1"
	assert 9999 >= apeID, f"{apeID} must be smaller than 10,000"

	data = {'owner': "", 'image': "", 'eyes': "" }
	
	#YOUR CODE HERE	
	bayc_contract = web3.eth.contract(address=contract_address,abi=abi)

	try:
		#get owner
		data['owner'] = bayc_contract.functions.ownerOf(apeID).call()
		
		#get tokenURI
		token_uri = bayc_contract.functions.tokenURI(apeID).call()
		token_uri = token_uri.replace('ipfs://', 'https://ipfs.io/ipfs/')
		
		#retrieve metadata from IPFS
		metadata = requests.get(token_uri)
		
		#parse
		metadata_json = metadata.json()
		
		#extract image uri
		image_uri = metadata_json.get("image")
		data['image'] = image_uri
		
		#extract eyes attribute
		eyes = None
		for attribute in metadata_json.get("attributes", []):
			if attribute.get("trait_type") == "Eyes":
				eyes = attribute.get("value")
				break
		data['eyes'] = eyes

	except Exception as e:
		print(f"Error retrieving Ape ID {apeID}: {e}")
		return data

	assert isinstance(data,dict), f'get_ape_info{apeID} should return a dict' 
	assert all( [a in data.keys() for a in ['owner','image','eyes']] ), f"return value should include the keys 'owner','image' and 'eyes'"
	return data

