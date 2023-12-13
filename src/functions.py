import json
from pathlib import Path
import src.exceptions as exceptions
from src.constants import LayerConfig
from src.data_collection import collect_data
from src.image_creation import build_layer_config, create_image_new, create_image_new_optimized
import time
from src.encoding import encode_img_to_b64


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

# -------------------------------------------------------------------------------------------------------------------- #

def get_layer_config(wallet):
        df = collect_data(wallet)

        for i in range(4):
            Config.LAYER_CONFIG[i][3] = []

        # change the radius in case wallet holds not enough to fill all circles
        if len(df) < 9:
            #Config.LAYER_CONFIG[1][0] = 285
            #Config.LAYER_CONFIG[1][1] = len(df) - 1
            nbr_layers = 2
        elif (len(df) > 9) & (len(df) < 24):
            Config.LAYER_CONFIG[1][0] = 250
            nbr_layers = 2
        elif (len(df) > 24) & (len(df) < 50):
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
