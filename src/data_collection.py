import json
import functools
from os import getenv
from dotenv import load_dotenv
from pandas import DataFrame
from src.constants import *
import src.exceptions
import requests
import pandas as pd

# populate values from local environment file
load_dotenv()

# API connection
graphQLEndpoint = "https://graphql.mainnet.stargaze-apis.com/graphql"


def check_address(address):
    # check if sg address exists -> return True else False
    return True


def get_address_to_sg_name(name):
    url = graphQLEndpoint
    body = ''' 
                {
                  name(name: "''' + str(name) + '''") {
                    associatedAddr
                  }
                }
                '''

    r = requests.post(url=url, json={"query": body})

    if r.status_code == 200:
        data = r.json()
        data = json.dumps(data)
        data = json.loads(data)
        return data['data']['name']['associatedAddr']

    return None


def check_sg_name(input):
    if input:
        if input[-6:] == ".stars":
            return True
    return False


def verify_wallet(address: str):
    try:
        if check_sg_name(address):
            print("name was submitted!")
            print(address[:-6])
            address = get_address_to_sg_name(address[:-6])
            print(address)
            return address
        elif address[0:5] == "stars":
            return address
        else:
            return False
    except:
        print("Error: verify_wallet")


def get_profil_pict(address):
    url = graphQLEndpoint

    body = '''
    {
          wallet(address: "''' + str(address) + '''") {
            name {
              media {
                visualAssets {
                  sm {
                    height
                    staticUrl
                    width
                  }
                }
              }
            }
          }    
    }
    '''

    r = requests.post(url=url, json={"query": body})
    print("response get_profil_pict:", r.text)

    if r.status_code == 200:
        data = r.json()
        data = json.dumps(data)
        data = json.loads(data)

        if data['data']['wallet']['name']:
            return data['data']['wallet']['name']['media']['visualAssets']['sm']['staticUrl']
        else:
            return None
    else:
        return None


def get_wallet_tokens(address) -> DataFrame:
    url = graphQLEndpoint
    offset = 0
    limit = 100
    df = pd.DataFrame()

    while True:
        print(offset)
        body = ''' 
                    {
                      tokens(ownerAddrOrName: "''' + str(address) + '''", limit: 100, offset: ''' + str(offset) + ''') {
                        tokens {
                          id
                          collection {
                            media {
                              visualAssets {
                                lg {
                                  staticUrl
                                }
                              }
                            }
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
            data = pd.json_normalize(data['data']['tokens']['tokens'])

            data[['address', 'token_id']] = data['id'].str.split('-', n=1, expand=True)
            data.drop(columns=['id'], inplace=True)

            data.rename(columns={'collection.media.visualAssets.lg.staticUrl': 'avatar_url'}, inplace=True)
            df = pd.concat([df, data], ignore_index=True)

            if len(data) < 100:
                return df
            else:
                offset += limit


def get_wallet_tokens_new(address) -> DataFrame:
    url = graphQLEndpoint
    body = ''' 
                    {
                      collectionCounts(owner: "''' + str(address) + '''", limit: 100) {
                        collectionCounts {
                          count
                          collection {
                            contractAddress
                            name
                            media {
                              visualAssets {
                                lg {
                                  staticUrl
                                }
                              }
                            }
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
        data = pd.json_normalize(data['data']['collectionCounts']['collectionCounts'])

        data.rename(
            columns={
                'collection.contractAddress': 'address',
                'collection.name': 'name',
                'collection.media.visualAssets.lg.staticUrl': 'avatar_url'
            },
            inplace=True
        )
        return data



def calc_score_collections(df: DataFrame) -> DataFrame:
    # agg and count the nbr of NFTs for each collection
    df = df.groupby('address', as_index=False).agg({'token_id': 'count', 'avatar_url': 'first'})
    df.rename(columns={'token_id': 'score'}, inplace=True)
    df['score'] = df['score'] / df['score'].sum() * 100
    df.to_csv("df.csv")
    return df


def collect_data(wallet: str) -> DataFrame:
    # returns a df which contains
    # - the user (address + profile pict link)
    # - all collections s/he is holding currently + nbr of respective NFTs

    address = verify_wallet(wallet)


    # create a df for the user
    df_center_user = pd.DataFrame([[address, get_profil_pict(address)]],
                                  columns=['address', 'avatar_url']
                                  )

    # df_collection_holdings = get_wallet_tokens(address)
    # df_collection_holdings_score = calc_score_collections(df_collection_holdings)
    # df_collection_holdings_score.sort_values(by="score", inplace=True, ascending=False)

    df_collection_holdings = get_wallet_tokens_new(address)


    df = pd.concat([df_center_user, df_collection_holdings], ignore_index=True)

    return df


get_wallet_tokens_new("stars1adr72atmnzzvqlfe574c3qk5s9zxk0l2gq2rz5")