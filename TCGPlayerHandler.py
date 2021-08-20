import requests
import json
import math
import TCG_TYPE
from pprint import pprint

class TCGPlayerHandler:

    # Init data
    def __init__(self, access_token, requested_tcg):
        self.access_token = access_token
        self.TOTAL_API_CALLS = 0
        self.requested_tcg = requested_tcg

    def increment_api_counter(self):
        self.TOTAL_API_CALLS += 1

    def reinit_api_counter(self):
        self.TOTAL_API_CALLS = 0

    # Request data on any single card
    def get_card_info(self, id):
        url = "https://api.tcgplayer.com/pricing/marketprices/" + id
        headers = {"Authorization": self.access_token}
        r = requests.request("GET", url, headers=headers)
        self.increment_api_counter()
        card_info = r.json()
        print('Card Info: ')
        print(card_info)

    # Generate a list of all sets.
    def get_all_sets(self):
        # Had to put together the two queries then remove some brackets in the resulting file to make the "allsets.json" file work
        url = "https://api.tcgplayer.com/catalog/categories/" + self.requested_tcg['id'] + "/groups"
        querystring1 = {"offset":"0","limit":"100"}
        headers = {"Authorization": self.access_token}
        r = requests.request("GET", url, headers=headers, params=querystring1)
        self.increment_api_counter()
        info = r.json()
        combined_info = []
        num_queries = math.ceil(info["totalItems"]/100)
        
        for x in range(0,num_queries):
            offset = x * 100
            querystring = {"offset":offset,"limit":"100"}
            headers = {"Authorization": self.access_token}
            r = requests.request("GET", url, headers=headers, params=querystring)
            self.increment_api_counter()
            temp_info = r.json()
            for i in temp_info["results"]:
                combined_info.append(i)     

        formatted_json = json.dumps(combined_info, indent=2)
        filename = self.requested_tcg['name'] + "AllSets.json"
        f = open(filename, "w")
        f.write(formatted_json)
        f.close()
        set_name_list = []
        for i in combined_info:
            set_name_list.append(i["name"])
        return set_name_list
    
    # Get the set ID of any set
    def get_set_id(self, set_name):
        setlistname = self.requested_tcg['name'] + "AllSets.json"
        f = open(setlistname)
        data = json.load(f)
        for i in data:
            if i["name"] == set_name:
                f.close()
                return i["groupId"]
        f.close()
        return None

    # Get the general info of all cards on any set
    def get_set_info(self, set_name, get_extended_fields):
        groupid = self.get_set_id(set_name)
        if groupid == None:
            print("Group ID not found")
            return None
        url = "https://api.tcgplayer.com/catalog/products"
        # querystring = {"groupId":groupid,"productTypes":"Cards","offset":"0","limit":"100"}
        querystring = {"groupId":groupid,"offset":"0","limit":"100"}
        headers = {"Authorization": self.access_token}
        r = requests.request("GET", url, headers=headers, params=querystring)
        self.increment_api_counter()
        info = r.json()
        num_queries = 6
        combined_info = []
        if "totalItems" in info:
            print(str(info["totalItems"]) + " cards found in the set...")
            num_queries = math.ceil(info["totalItems"]/100)
        else:
            print("Total Items Not found")        
        
        for x in range(0,num_queries):
            offset = x * 100
            url = "https://api.tcgplayer.com/catalog/products"
            querystring = {"groupId":groupid,"offset":offset,"limit":"1000","getExtendedFields":get_extended_fields}
            # querystring = {"groupId":groupid,"productTypes":"Cards","offset":offset,"limit":"100","getExtendedFields":get_extended_fields}
            headers = {"Authorization": self.access_token}
            r = requests.request("GET", url, headers=headers, params=querystring)
            self.increment_api_counter()
            temp_info = r.json()
            for i in temp_info["results"]:
                # pprint(i) #debugging
                combined_info.append(i)
        return combined_info

    # Get the price info of all cards in any set
    def get_set_price_info(self, groupid):
        url = "https://api.tcgplayer.com/pricing/group/" + groupid
        headers = {"Authorization": self.access_token}
        r = requests.request("GET", url, headers=headers)
        self.increment_api_counter()
        info = r.json()
        formatted_info = json.dumps(info, indent=2)
        return formatted_info

    # Generate Dictionary of Cards matched with their product IDs
    def get_set_products(self, set_list):
        products_list = []
        for i in set_list:
            products_list.append({"productId": i["productId"], "Card Name": i["name"]})  
        return products_list

    # for each batch of 100 ids, create a new search string
    # divide total number of ids by 100
    def get_products_price_info(self, product_list):
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
            headers = {"Authorization": self.access_token}
            r = requests.request("GET", url, headers=headers)
            self.increment_api_counter()
            r_temp = r.json()
            for i in r_temp["results"]:
                info.append(i)
        return info

    # Generates and conglomorates all data of each card for a given set.
    def generate_all_set_data(self, set_name, write_to_file):
        get_extended_fields = True
        set_info = self.get_set_info(set_name, get_extended_fields)
        if set_info == None:
            print("Could not find set")
            return None
        product_list = self.get_set_products(set_info)
        price_info = self.get_products_price_info(product_list)

        all_data = []
        for j in set_info:
            for i in price_info:
                if i["productId"] == j["productId"] and (i["marketPrice"] is not None or i["lowPrice"] is not None or i["midPrice"] is not None or i["highPrice"] is not None):
                    i.update(j)
                    i["setName"] = set_name
                    i["searchable"] = i["name"] + " " + set_name + " " + i["subTypeName"]
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
    