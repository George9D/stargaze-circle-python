import json
from pathlib import Path
import src.exceptions as exceptions
from src.constants import LayerConfig
from src.data_collection import collect_data
from src.image_creation import build_layer_config, create_image_old, create_image_new

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


def main(debug: bool = False):

    d = Path("res/circles_dump.json").resolve()
    i = Path("res/circles_md.png").resolve()
    p = Path("res/placeholder_avatar.png").resolve()

    try:
        if debug and d.exists():
            q = Path("res/debug_avatar.jpg").resolve()
            with open(d, "r") as f:
                lc = json.load(f)
        else:
            q = None

            # new version - pandas df
            df = collect_data(Config.WALLET)

            # new version - pandas df
            lc = build_layer_config(df, Config.LAYER_CONFIG)
            print(lc)

            #with open(d, "w") as f:
            #    json.dump(lc, f)

        image = create_image_old(Config.BG_SIZE, Config.BG_CLR, lc, q)
        # image = create_image_new(Config.BG_SIZE, Config.BG_CLR, lc, q)
        image.save(i, "PNG")
        #print(image)

        # data_str = encode_img_to_b64(image)
        return image

    except (exceptions.InvalidUser, exceptions.ApiError) as e:
        print(e)

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
