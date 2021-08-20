from pymongo import MongoClient
import pymongo
from datetime import datetime
import os
import json

DB_UPDATER_NAME = "DbUpdateInfo"

def get_new_coll_name():
  now = datetime.now()
  current_date = now.strftime("%Y-%m-%d")
  dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
  coll_name = "TEST - Cards " + dt_string

  return coll_name, current_date

def get_card_data():
  f = open("PokemonAllSetsData.json","r")
  card_data = json.load(f)
  f.close()

  return card_data

def get_db_client():
  MongoUsername = os.environ["MongoUsername"]
  MongoPassword = os.environ["MongoPassword"]
  MongoUrl = os.environ["MongoUrl"]
  connectionURI = f"mongodb+srv://{MongoUsername}:{MongoPassword}@{MongoUrl}/"
  client = MongoClient(connectionURI)

  return client

def slim_collection(coll):
  remove_list = ["lowPrice", "highPrice", "directLowPrice", "cleanName", "imageUrl", "categoryId", "url", "modifiedOn", "imageCount", "presaleInfo", "extendedData", "searchable", "setName"]
  for entry in remove_list:
    coll.update_many({}, {'$unset': {entry:1}});

def add_to_update_db(_db_update_coll, _t_name, _t_date, _prev_table_data):
  """ 
  Update the table that the website will be checking to determine which
  collection should be used to get the current card data.
  Table format:
  Index | Collection Name | Collection Date
  """

  t_name = _t_name
  t_date = _t_date
  prev_data = _prev_table_data

  coll = _db_update_coll

  index = prev_data["index"] + 1

  collection_obj = {
    "index": index,
    "Collection Name": t_name,
    "Collection Date": t_date
  }

  coll.insert_one(collection_obj)

def get_latest_table(coll):
  collection = coll
  return collection.find().sort('index', pymongo.DESCENDING)[0]

def run_full_db_updates():
  db_client = get_db_client()
  db = db_client['PokeCollector']

  # Get Current Card Data from json and make new Collection
  new_coll_name, current_date = get_new_coll_name()
  collection = db[new_coll_name]
  collection.insert_many(get_card_data())

  db_update_coll = db[DB_UPDATER_NAME]

  # Add new Collection to current table tracker
  last_table_data = get_latest_table(db_update_coll)
  add_to_update_db(db_update_coll, new_coll_name, current_date, last_table_data)

  # Slim old card table
  prev_coll = db[last_table_data["Collection Name"]]
  slim_collection(prev_coll)

  db_client.close()