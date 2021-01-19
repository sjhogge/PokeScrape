import requests
import json
import math
import time

# use this to gauge how often we are calling the API
# because we are limited to 300 calls per minute
TOTAL_API_CALLS = 0

# put this function below any api call.
def increment_api_counter():
  global TOTAL_API_CALLS
  TOTAL_API_CALLS += 1

# Pulls the most recent access token from the "API_Access.json" file
def get_current_access_token():
  f = open("API_Access.json","r")
  client_info = json.load(f)
  f.close() 
  access_token = client_info["Access Token"]
  return access_token

# Request data on any single card
def get_card_info(access_token, id):
  url = "https://api.tcgplayer.com/pricing/marketprices/" + id
  _access_token = access_token
  headers = {"Authorization": _access_token}
  r = requests.request("GET", url, headers=headers)
  increment_api_counter()
  card_info = r.json()
  print('Card Info: ')
  print(card_info)

# Generate a list of all sets, run this to update.
def get_all_sets(access_token):
  # Had to put together the two queries then remove some brackets in the resulting file to make the "allsets.json" file work
  url = "https://api.tcgplayer.com/catalog/categories/3/groups"
  querystring1 = {"offset":"0","limit":"100"}
  querystring2 = {"offset":"100","limit":"100"}
  headers = {"Authorization": access_token}
  sets = []
  r = requests.request("GET", url, headers=headers, params=querystring1)
  increment_api_counter()
  info = r.json()
  combined_info = []
  num_queries = math.ceil(info["totalItems"]/100)
  for x in range(0,num_queries):
    offset = x * 100
    querystring = {"offset":offset,"limit":"100"}
    headers = {"Authorization": access_token}
    r = requests.request("GET", url, headers=headers, params=querystring)
    increment_api_counter()
    temp_info = r.json()
    for i in temp_info["results"]:
      combined_info.append(i)

  formatted_json = json.dumps(combined_info, indent=2)
  f = open("AllSets.json", "w")
  f.write(formatted_json)
  f.close()
  # print(combined_info)
  set_name_list = []
  for i in combined_info:
    set_name_list.append(i["name"])
  # print(set_name_list)
  return set_name_list

# Get the general info of all cards on any set
def get_set_info(access_token, set_name):
  groupid = get_set_id(set_name)
  if groupid == None:
    return None
  url = "https://api.tcgplayer.com/catalog/products"
  querystring = {"groupId":groupid,"productTypes":"Cards","offset":"0","limit":"100"}
  headers = {"Authorization": access_token}
  r = requests.request("GET", url, headers=headers, params=querystring)
  increment_api_counter()
  info = r.json()
  combined_info = []
  if "totalItems" not in info:
    return None
  print(str(info["totalItems"]) + " cards found in the set...")
  num_queries = math.ceil(info["totalItems"]/100)
  for x in range(0,num_queries):
    offset = x * 100
    url = "https://api.tcgplayer.com/catalog/products"
    querystring = {"groupId":groupid,"productTypes":"Cards","offset":offset,"limit":"100"}
    headers = {"Authorization": access_token}
    r = requests.request("GET", url, headers=headers, params=querystring)
    increment_api_counter()
    temp_info = r.json()
    for i in temp_info["results"]:
      combined_info.append(i)

  formatted_info = json.dumps(combined_info,indent=2)
  return combined_info

# Get the price info of all cards in any set
def get_set_price_info(access_token, groupid):
  url = "https://api.tcgplayer.com/pricing/group/" + groupid
  headers = {"Authorization": access_token}
  r = requests.request("GET", url, headers=headers)
  increment_api_counter()
  info = r.json()
  formatted_info = json.dumps(info, indent=2)
  # print(formatted_info)
  return formatted_info

# Get the set ID of any set
def get_set_id(set_name):
  f = open("AllSets.json")
  data = json.load(f)
  for i in data:
    #print("Set Name: " + i["name"] + " --> " + "Set ID: " + str(i["groupId"]))
    if i["name"] == set_name:
      id = i["groupId"]
      f.close()
      return i["groupId"]
  f.close()
  return None

# Generate Dictionary of Cards matched with their product IDs
def get_set_products(set_list):
  products_list = []
  for i in set_list:
    products_list.append({"productId": i["productId"], "Card Name": i["name"]})  
  # print (products_list)  
  return products_list

# for each batch of 100 ids, create a new search string
# divide total number of ids by 100
def get_products_price_info(access_token, product_list):
  productids = []
  appender = "%2C"
  info = []
  for i in product_list:
    productids.append(str(i["productId"]))
  num_queries = math.ceil(len(productids)/100)
  for x in range(0,num_queries):
    temp_ids = []
    if x == num_queries:
      temp_ids = productids[num_queries*100:]
    else:
      start_index = x*100
      stop_index = (x+1)*100-1
      temp_ids = productids[start_index:stop_index]
    temp_ids_string = ""
    for i in temp_ids:
      temp_ids_string += i + appender
    temp_ids_string = temp_ids_string[:-3]
    url = "https://api.tcgplayer.com/pricing/product/" + temp_ids_string
    headers = {"Authorization": access_token}
    r = requests.request("GET", url, headers=headers)
    increment_api_counter()
    r_temp = r.json()
    for i in r_temp["results"]:
      info.append(i)
    # formatted_info = json.dumps(info, indent=2)
    # print(formatted_info)
  return info

# Generates and conglomorates all data of each card for a given set.
def generate_all_set_data(access_token, set_name, write_to_file):
  set_info = get_set_info(access_token, set_name)
  if set_info == None:
    print("Could not find set")
    return None
  product_list = get_set_products(set_info)
  price_info = get_products_price_info(access_token,product_list)

  all_data = []
  for j in set_info:
    for i in price_info:
      if i["productId"] == j["productId"] and (i["marketPrice"] is not None or i["lowPrice"] is not None or i["midPrice"] is not None or i["highPrice"] is not None):
        i.update(j)
        all_data.append(i)
  all_data_f = json.dumps(all_data, indent=2)
  # print(all_data_f)
  if write_to_file:
    filename = "SetData/" + set_name + ".json"
    filename = filename.replace(":", "")
    f = open(filename, "w")
    f.write(all_data_f)
    f.close()
    print("Data written for " + set_name)
  return all_data

if __name__ == "__main__":
  ACCESS_TOKEN = get_current_access_token()
  set_name = "SM Promos"
  write_set_to_file = False
  
  start_time = int(round(time.time() * 1000))
  all_sets_list = get_all_sets(ACCESS_TOKEN)
  for i in all_sets_list:
    print(i)
    generate_all_set_data(ACCESS_TOKEN, i, write_set_to_file)
    print ("-----")
    # time.sleep(0.25) # Make sure to limit the number of API calls just in case
  end_time = int(round(time.time() * 1000))
  total_time = (end_time - start_time)/(1000*60)
  print("Time (minutes): " + str(round(total_time, 2)))
  print("Total API calls: " + str(TOTAL_API_CALLS))
  calls_per_minute = TOTAL_API_CALLS/total_time
  print("Number of calls per minute: " + str(round(calls_per_minute, 2)))

  '''
  What next?
  - Combine all set data into one giant datasheet to be able to pull data from multiple sets in one request
  - Create a way for someone to create a list of their cards, and be able to pull data on those cards
  '''
