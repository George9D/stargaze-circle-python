import json
from pathlib import Path
import src.exceptions as exceptions
from src.constants import LayerConfig
from src.data_collection import collect_data
from src.image_creation import build_layer_config, create_image_new, create_image_new_optimized
import time
from src.encoding import encode_img_to_b64


class Config:
    # Twitter WALLET to scan
    # WALLET = "stars1xuwl7x8htyl26t7pe3l0x6auj3j9jwd2k26qx5"
    WALLET = "stars1adr72atmnzzvqlfe574c3qk5s9zxk0l2gq2rz5"
    # WALLET = "stars1p655nr52wepstj39jr3skwv6nkmdrfka3e96ym"
    # hex of the desired background color
    # BG_CLR = "#448dd9"
    BG_CLR = "rgba(255, 255, 255, 0)"
    # (height, width)
    BG_SIZE = (1000, 1000)
    # layer config constants
    # [[layer radius, number of users in the layer, gap size], ...]
    LAYER_CONFIG: LayerConfig = [
        [0, 1, 0],
        [200, 8, 25],
        [330, 15, 25],
        [450, 26, 20],
    ]

# -------------------------------------------------------------------------------------------------------------------- #

def get_layer_config(wallet):
        df = collect_data(wallet)

        # new version - pandas df
        lc = build_layer_config(df, Config.LAYER_CONFIG)

        return lc

def create_image(lc, bg_color):
    p = Path("res/placeholder_avatar.png").resolve()
    q = None
    image = create_image_new(Config.BG_SIZE, bg_color, lc, q)
    return image

# -------------------------------------------------------------------------------------------------------------------- #
