import requests, json

#https://gist.github.com/CptSpaceToaster/bf7464602aca07260d083a7747aaef97

def get_token():
    # Open the API_Access.json file to get public and private key
    f = open("API_Access.json","r")
    client_info = json.load(f)
    f.close()
    # client_info = access_data["access_data"]
    client_id = client_info["Public Key"]
    client_secret = client_info["Private Key"]

    # Make request for bearer token
    url = "https://api.tcgplayer.com/token"
    data = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    r = requests.post(url, data=data)

    # Parse JSON from request and build access_token
    access_token_response = r.json()
    access_token = access_token_response['token_type'] + ' ' + access_token_response['access_token']
    client_info["Access Token"] = access_token
    client_info_json = json.dumps(client_info, indent=2)

    # Write access_token back to file
    f = open("API_Access.json", "w")
    f.write(client_info_json)
    f.close()

# Pulls the most recent access token from the "API_Access.json" file
def get_current_access_token():
    f = open("API_Access.json","r")
    client_info = json.load(f)
    f.close() 
    access_token = client_info["Access Token"]
    return access_token

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
    