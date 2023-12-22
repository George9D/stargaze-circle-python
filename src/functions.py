import datetime
import json
from pathlib import Path

import numpy as np

import src.exceptions as exceptions
from src.constants import LayerConfig
from src.data_collection import collect_data
from src.image_creation import build_layer_config, create_image_new, create_image_new_optimized
import time
from src.encoding import encode_img_to_b64
import requests
import pandas as pd

class Config:
    WALLET = "stars1adr72atmnzzvqlfe574c3qk5s9zxk0l2gq2rz5"
    # BG_CLR = "#448dd9"
    BG_CLR = "rgba(255, 255, 255, 0)"
    BG_SIZE = (1000, 1000)
    # layer config constants
    # [[layer radius, number of users in the layer, gap size], ...]
    LAYER_CONFIG: LayerConfig = [
            [0, 1, 0, [], 0],
            [200, 7, 25, [], 1],
            [330, 13, 25, [], 2],
            [450, 21, 20, [], 5],
        ]

"""    
    LAYER_CONFIG: LayerConfig = [
        [0, 1, 0, [], 0],
        [200, 8, 25, [], 0],
        [330, 15, 25, [], 0],
        [450, 26, 20, [], 0],
    ]
"""

graphQLEndpoint = "https://graphql.mainnet.stargaze-apis.com/graphql"

# -------------------------------------------------------------------------------------------------------------------- #

def get_layer_config(wallet):
        df = collect_data(wallet)

        for i in range(4):
            Config.LAYER_CONFIG[i][3] = []

        # change the radius in case wallet holds not enough to fill all circles
        if len(df) < 8:
            #Config.LAYER_CONFIG[1][0] = 285
            #Config.LAYER_CONFIG[1][1] = len(df) - 1
            nbr_layers = 2
        elif (len(df) > 8) & (len(df) <= 21):
            Config.LAYER_CONFIG[1][0] = 250
            nbr_layers = 2
        elif (len(df) > 21) & (len(df) < 50):
            Config.LAYER_CONFIG[1][0] = 225
            Config.LAYER_CONFIG[2][0] = 375
            nbr_layers = 3
        else:
            Config.LAYER_CONFIG[1][0] = 200
            Config.LAYER_CONFIG[2][0] = 330
            Config.LAYER_CONFIG[3][0] = 450
            nbr_layers = 4

        # new version - pandas df
        lc = build_layer_config(df, Config.LAYER_CONFIG[:nbr_layers])

        return lc

def create_image(lc, bg_color):
    p = Path("res/placeholder_avatar.png").resolve()
    q = None
    image = create_image_new(Config.BG_SIZE, bg_color, lc, q)
    return image

# -------------------------------------------------------------------------------------------------------------------- #


def query_wallet(string):
    url = graphQLEndpoint
    body = ''' 
                    {
                      wallets(searchQuery: "''' + str(string) + '''") {
                          wallets {
                              address
                              name {
                                associatedAddr
                                name
                              }
                            }
                      }
                    }
        '''

    r = requests.post(url=url, json={"query": body})

    if r.status_code == 200:
        data = r.json()
        data = json.dumps(data)
        data = json.loads(data)

        data = pd.json_normalize(data['data']['wallets']['wallets'])
        wallets = []

        data.sort_values(by="address", inplace=True)

        for idx, d in data.iterrows():
            # check if name exists, if so return name, else the address
            if d['name.name'] is np.NAN:
                wallets.append(d['address'])
            else:
                # address = data['data']['wallets']['wallets']['name']['associatedAddr']
                wallets.append(d['name.name'])

        return wallets


"""def check_if_wallet_exists(input: str):
    url = graphQLEndpoint

    # check if .stars ending and remove
    if input[-6:] == ".stars":
        input = input[:-6]

    body = ''' 
                    {
                      wallets(searchQuery: "''' + input + '''") {
                          wallets {
                              address
                              name {
                                associatedAddr
                                name
                              }
                            }
                      }
                    }
        '''

    r = requests.post(url=url, json={"query": body})

    if r.status_code == 200:
        data = r.json()
        data = json.dumps(data)
        data = json.loads(data)

        data = pd.json_normalize(data['data']['wallets']['wallets'])

        # check if name/address exists and is unique
        if data.empty:
            return False
        elif input in data['address'].values:
            return data[data['address'] == input]['address'].values[0]
        elif "name.name" in data.keys() and input in data['name.name'].values:
            return data[data['name.name'] == input]['address'].values[0]
        else:
            return False"""


def check_if_wallet_exists(input: str):
    url = graphQLEndpoint

    # check if .stars ending and remove
    if input[-6:] == ".stars":
        input = input[:-6]

    body = ''' 
                    {
                      wallet(address: "''' + input + '''") {
                              stats {
                                address
                              }
                      }
                    }
        '''

    r = requests.post(url=url, json={"query": body})

    if r.status_code == 200:
        data = r.json()
        data = json.dumps(data)
        data = json.loads(data)


        if data['data']['wallet']['stats']:
            return data['data']['wallet']['stats']['address']
        else:
            return False



def get_traits(collection: str) -> pd.DataFrame:
    url = "https://constellations-api.mainnet.stargaze-apis.com/graphql"

    body = ''' 
                    {
                      collectionTraits(collectionAddr: "''' + collection + '''"){
                        name,
                        values{
                          value
                        }
                      }
                    }
        '''

    r = requests.post(url=url, json={"query": body})

    if r.status_code == 200:
        data = r.json()
        data = json.dumps(data)
        data = json.loads(data)

        df = pd.json_normalize(data['data']['collectionTraits'], "values", ['name'])
        return df


def get_current_holders(collection: str) -> pd.DataFrame:
    url = "https://constellations-api.mainnet.stargaze-apis.com/graphql"
    offset = 0
    DF = pd.DataFrame()

    while True:
        body = ''' 
                        {
                        tokens(collectionAddr: "''' + collection + '''", offset: ''' + str(offset) + ''', limit: 100){
                              tokens{
                                tokenId
                                ownerAddr
                              }
                          }
                        }
            '''

        r = requests.post(url=url, json={"query": body})

        if r.status_code == 200:
            data = r.json()
            data = json.dumps(data)
            data = json.loads(data)

            df = pd.json_normalize(data['data']['tokens']['tokens'])
            DF = pd.concat([DF, df], ignore_index=True)

        if len(df) < 100:
            return DF
        else:
            offset += 100


def get_current_holders_by_trait(collection: str, trait: str, value: str) -> pd.DataFrame:
    url = "https://constellations-api.mainnet.stargaze-apis.com/graphql"
    offset = 0
    DF = pd.DataFrame()

    while True:
        body = ''' 
                        {
                        tokens(collectionAddr: "''' + collection + '''",
                            filterByTraits: {name: "''' + trait + '''", value: "''' + value + '''"}, offset: ''' + str(offset) + ''', limit: 100){
                              tokens{
                                tokenId
                                ownerAddr
                              }
                          }
                        }
            '''

        r = requests.post(url=url, json={"query": body})

        if r.status_code == 200:
            data = r.json()
            data = json.dumps(data)
            data = json.loads(data)

            df = pd.json_normalize(data['data']['tokens']['tokens'])
            DF = pd.concat([DF, df], ignore_index=True)

        if len(df) < 100:
            return DF
        else:
            offset += 100


def get_minters_first(collection: str, number: int) -> pd.DataFrame:
    pass

def get_minters_last(collection: str, number: int) -> pd.DataFrame:
    pass

def get_minters_date_range(collection: str, startDate: datetime.datetime, endDate: datetime.datetime) -> pd.DataFrame:
    pass


def get_mints_first(collection: str, number: int) -> pd.DataFrame:
    pass

def get_mints_last(collection: str, number: int) -> pd.DataFrame:
    pass

def get_mints_date_range(collection: str, startDate: datetime.datetime, endDate: datetime.datetime) -> pd.DataFrame:
    pass
