import requests
import json
import math
import time
import os
import TCG_TYPE 
import token_handler

# use this to gauge how often we are calling the API
# because we are limited to 300 calls per minute
TOTAL_API_CALLS = 0

# put this function below any api call.
def increment_api_counter():
  global TOTAL_API_CALLS
  TOTAL_API_CALLS += 1

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
def get_all_sets(access_token, requested_tcg):
  # Had to put together the two queries then remove some brackets in the resulting file to make the "allsets.json" file work
  url = "https://api.tcgplayer.com/catalog/categories/" + requested_tcg['id'] + "/groups"
  querystring1 = {"offset":"0","limit":"100"}
  headers = {"Authorization": access_token}
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
  filename = requested_tcg['name'] + "AllSets.json"
  f = open(filename, "w")
  f.write(formatted_json)
  f.close()
  set_name_list = []
  for i in combined_info:
    set_name_list.append(i["name"])
  return set_name_list

# Get the general info of all cards on any set
def get_set_info(access_token, set_name, requested_tcg):
  groupid = get_set_id(set_name, requested_tcg)
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
def get_set_id(set_name, requested_tcg):
  setlistname = requested_tcg['name'] + "AllSets.json"
  f = open(setlistname)
  data = json.load(f)
  for i in data:
    if i["name"] == set_name:
      f.close()
      return i["groupId"]
  f.close()
  return None

# Generate Dictionary of Cards matched with their product IDs
def get_set_products(set_list):
  products_list = []
  for i in set_list:
    products_list.append({"productId": i["productId"], "Card Name": i["name"]})  
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
  return info

# Generates and conglomorates all data of each card for a given set.
def generate_all_set_data(access_token, set_name, write_to_file, requested_tcg):
  set_info = get_set_info(access_token, set_name, requested_tcg)
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
        i["setName"] = set_name
        all_data.append(i)
  all_data_f = json.dumps(all_data, indent=2)
  if write_to_file:
    filename = "SetData/" + set_name + ".json"
    filename = filename.replace(":", "")
    f = open(filename, "w")
    f.write(all_data_f)
    f.close()
    print("Data written for " + set_name)
  return all_data

if __name__ == "__main__":

  ######### THIS IS THE TCG YOU WANT TO PULL DATA ON ########
  # Current options are POKEMON, YUGIOH, and MAGIC

  REQUESTED_TCG = TCG_TYPE.TCG_Type.POKEMON
  # REQUESTED_TCG = TCG_TYPE.TCG_Type.YUGIOH
  # REQUESTED_TCG = TCG_TYPE.TCG_Type.MAGIC

  #########################################################

  ACCESS_TOKEN = token_handler.token_check()
  # write_set_to_file = False
  write_all_sets_to_file = True
  
  start_time = int(round(time.time() * 1000))
  all_sets_list = get_all_sets(ACCESS_TOKEN, REQUESTED_TCG)
  all_sets_data = []

  for i in all_sets_list:
    print(i)
    current_set_data = generate_all_set_data(ACCESS_TOKEN, i, False, REQUESTED_TCG)
    if current_set_data is not None:
     all_sets_data = all_sets_data + current_set_data
    print ("-----")

  if write_all_sets_to_file:
    filename = REQUESTED_TCG['name'] + "AllSetsData"
    filename_json = filename + ".json"
    filename_csv = filename + ".csv"
    f = open(filename_json, "w+")
    all_sets_data_f = json.dumps(all_sets_data, indent=2)
    f.write(all_sets_data_f)
    f.close()
    print("Data written for all " + REQUESTED_TCG['name'] + " sets")

  end_time = int(round(time.time() * 1000))
  total_time = (end_time - start_time)/(1000*60)
  print("Time (minutes): " + str(round(total_time, 2)))
  print("Total API calls: " + str(TOTAL_API_CALLS))
  calls_per_minute = TOTAL_API_CALLS/total_time
  print("Number of calls per minute: " + str(round(calls_per_minute, 2)))

  ## TO DO ##
  # Probably add more comments
  # Add more TCGs to the TCG_TYPE class
  # Make the requests faster without going over the limit of requests designated by TCGPlayer
  # Moar Error Handling!!!
