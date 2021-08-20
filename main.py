from TCGPlayerHandler import TCGPlayerHandler
from TCG_TYPE import TCG_Type
from MongoDatabaseHandler import run_full_db_updates
from emailer import send_email
import TokenHandler
import time
import json

def write_all_sets_to_file(tcgplayer, all_sets_data):
    filename = tcgplayer.requested_tcg['name'] + "AllSetsData"
    filename_json = filename + ".json"
    #filename_csv = filename + ".csv"
    f = open(filename_json, "w+")
    all_sets_data_f = json.dumps(all_sets_data, indent=2)
    f.write(all_sets_data_f)
    f.close()
    print("Data written for all " + tcgplayer.requested_tcg['name'] + " sets")


def full_update():
  ######### THIS IS THE TCG YOU WANT TO PULL DATA ON ########
  # Current options are POKEMON, YUGIOH, and MAGIC

  requested_tcg = TCG_Type.POKEMON
  # requested_tcg = TCG_Type.YUGIOH
  # requested_tcg = TCG_Type.MAGIC

  #########################################################

  access_token = TokenHandler.token_check()
  tcgplayer = TCGPlayerHandler(access_token, requested_tcg)
  write_to_file = True

  start_time = int(round(time.time() * 1000))
  all_sets_list = tcgplayer.get_all_sets()
  all_sets_data = []

  for i in all_sets_list:
      print(i)
      current_set_data = tcgplayer.generate_all_set_data(i, False)
      if current_set_data is not None:
          all_sets_data = all_sets_data + current_set_data
      print ("-----")

  if write_to_file:
      write_all_sets_to_file(tcgplayer, all_sets_data)

  end_time = int(round(time.time() * 1000))
  total_time = (end_time - start_time)/(1000*60)
  print("Time (minutes): " + str(round(total_time, 2)))
  print("Total API calls: " + str(tcgplayer.TOTAL_API_CALLS))
  calls_per_minute = tcgplayer.TOTAL_API_CALLS/total_time
  print("Number of calls per minute: " + str(round(calls_per_minute, 2)))

  print("Running Database Updates")
  start_time = int(round(time.time() * 1000))
  run_full_db_updates()
  end_time = int(round(time.time() * 1000))
  total_time = (end_time - start_time)/(1000*60)
  print("Time (minutes): " + str(round(total_time, 2)))

  message = "Pokecove Databases have been updated!"
  send_email(message)


if __name__ == "__main__":

  full_update()

  ## TO DO ##
  # Use set name from extended field instead of groupID
  # Probably add more comments
  # Add more TCGs to the TCG_TYPE class
  # Make the requests faster without going over the limit of requests designated by TCGPlayer
  # Moar Error Handling!!!