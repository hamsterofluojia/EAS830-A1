import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE

	#convert the dictionary to json
	data_json = json.dumps(data)

	#define headers
	headers = {
		'pinata_api_key': '3330181a4141c283e7a6',
		'pinata_secret_api_key':'2efca1e92a3d499e20d8a68e01e0c5d9839f37b4be11f9727d34b0cdd8299934'
	}

	url = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'

	#upload data
	response = requests.post(url, headers=headers, json=data_json)

	if response.status_code == 200:
		cid = response.json()['IpfsHash']
		print(f'Successfully uploaded to IPFS with hash: {cid}')
		return cid

	else:
		print('Failed to upload to IPFS:', response.text)
		return None


def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	

	#construct url
	url = f'https://ipfs.io/ipfs/{cid}'

	try:
		response = requests.get(url)

		if response.status_code == 200:
			data = response.json()
			assert isinstance(data,dict), f"get_from_ipfs should return a dict"
			return data

		else:
			print(f'failed to fetch data from ipfs')
			return None

		# If attempt failed, throw an exception
  	except requests.exceptions.RequestException as e:
		print(f'An error occurred: {e}')
    		return None
