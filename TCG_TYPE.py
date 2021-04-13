# this is a pseudo-enum so that you can pick which tcg you wanna pull data from
# theoretically in the future all TCGs from TCGPlayer will be added here

class TCG_Type:
  MAGIC = {"id": "1", "name": "Magic"}
  YUGIOH = {"id": "2", "name": "Yugioh"}
  POKEMON = {"id": "3", "name": "Pokemon"}