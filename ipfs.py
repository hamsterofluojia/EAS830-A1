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
    'pinata_secret_api_key': '2efca1e92a3d499e20d8a68e01e0c5d9839f37b4be11f9727d34b0cdd8299934',
  }

	url = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'

	#upload data
	response = requests.post(
    url,
    headers=headers,
    json=data_json
  )

	if response.status_code == 200:
    cid = response.json()['IpfsHash']
    print(f'Successfully uploaded to IPFS with hash: {cid}')
    return cid

  else:
    print('Failed to upload to IPFS:', response.text)
    return None

	"""
	api key = 3330181a4141c283e7a6
	api secret key = 2efca1e92a3d499e20d8a68e01e0c5d9839f37b4be11f9727d34b0cdd8299934

	const JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI2NTcyM2IyZS05MDZkLTQwNTAtODQ2Zi05Y2Y3MDYwN2E4N2UiLCJlbWFpbCI6ImthdGV0aWFuQHNlYXMudXBlbm4uZWR1IiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjMzMzAxODFhNDE0MWMyODNlN2E2Iiwic2NvcGVkS2V5U2VjcmV0IjoiMmVmY2ExZTkyYTNkNDk5ZTIwZDhhNjhlMDFlMGM1ZDk4MzlmMzdiNGJlMTFmOTcyN2QzNGIwY2RkODI5OTkzNCIsImV4cCI6MTc2MDkyODkyNn0.i1VM9FrVgcqNN4xIZJk73kVxNxEJtff9dYC232n1N0g'


	url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
	headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "multipart/form-data"
	}
	response = requests.request("POST", url, data=data, headers=headers)
	print(response.text)
	cid = response."IpfsHash"
"""

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	

	#construct url
	url = f'https://ipfs.io/ipfs/{cid}'

	try:
        # Make attempt to GET content from url
        response = requests.get(url)
        
        # Check for successful response
        if response.status_code == 200:
						assert isinstance(data,dict), f"get_from_ipfs should return a dict"
            return data

				# if response was not successful
        else:
            print(f'Failed to fetch data from IPFS: {response.status_code} - {response.text}')
            return None

		# If attempt failed, throw an exception
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')
        return None
