from TCGPlayerHandler import TCGPlayerHandler
from TCG_TYPE import TCG_Type
import TokenHandler
import time
import json
from pprint import pprint

requested_tcg = TCG_Type.POKEMON
access_token = TokenHandler.token_check()
tcgplayer = TCGPlayerHandler(access_token, requested_tcg)
set_name = "Base Set (Shadowless)"
set_info = tcgplayer.get_set_info(set_name, True)