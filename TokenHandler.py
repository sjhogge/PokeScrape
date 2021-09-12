import requests, json
import os
from DotEnvHandler import set_environ

set_environ()

#https://gist.github.com/CptSpaceToaster/bf7464602aca07260d083a7747aaef97

def get_token(): 
  client_id = os.environ["Public Key"]
  client_secret = os.environ["Private Key"]
  
  # Make request for bearer token
  url = "https://api.tcgplayer.com/token"
  data = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
  r = requests.post(url, data=data)

  # Parse JSON from request and build access_token
  access_token_response = r.json()
  access_token = access_token_response['token_type'] + ' ' + access_token_response['access_token']

  os.environ["Access Token"] = access_token

# Pulls the most recent access token from the "API_Access.json" file
def get_current_access_token():

  return os.environ["Access Token"]

# Runs a call to TCGplayer to check if current token is valid
def is_token_valid():
  try:
    access_token = get_current_access_token()
    url = "https://api.tcgplayer.com/catalog/conditions/"
    headers = {"Authorization": access_token}
    r = requests.request("GET", url, headers=headers)
    info = r.json()
    valid = info['success']
    if not valid:
      print("Access Token not valid.")
    return valid
  except KeyError:
    print("Access Token not found.")
    return False
  except:
    print("Undefined error.")
    return False

def token_check():
    if not is_token_valid():
        print("Retrieving new token.")
        get_token()
    else:
        print("Token is valid.")
    access_token = get_current_access_token()
    return access_token
    

if __name__ == "__main__":
    token_check()
    