# PokeScrape
This code will request all pokemon card data from TCGPlayer and combine it all into a single JSON file called "AllSetsData.json"

In order to get started, you'll want to create a json file called API_Access.json in the same folder as main.py. It should have the following in it:

{
  "Application ID": "{Your application ID}",
  "Public Key": "{Your Public Key}",
  "Private Key": "{Your Private Key}"
}


The application ID, Public Key, and Private Key will be obtained from TCGPlayer through an application found here:
http://developer.tcgplayer.com/developer-application-form.html


You will need to install the requests library to get this to work correctly:
pip install requests

Once you get everything set up, all you have to do is run 'main.py' and *hopefully* you will start receiving all the current data from TCGPlayer! I've also added the capability to grab all the set data for Yugioh and Magic as well, if you enable it in main.py.

If you have any question let me know on Discord here: BrooKlynOtter#1942
I probably should have added more comments....

Oh yeah, if you end up using this for something let me know what you are doing with it!! This was just a fun project to learn more about the REST API and how to make requests through python. If you want you can totally follow or sub to me on Twitch here: https://www.twitch.tv/BrooKlynOtter
