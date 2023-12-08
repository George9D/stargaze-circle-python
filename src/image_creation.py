import math
from io import BytesIO
from pathlib import Path
from typing import Union

import requests
from PIL import Image, ImageDraw
from src.constants import *

COMMON_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}


def build_layer_config(data, layer_config: LayerConfig) -> list:
    print("build_layer_confi")
    # creates as a list containing different layers as separate dfs
    #layer_config[x][1] contains the nbr of collections contained in this layer

    prev_col_idx = 1
    layer_config[0].append(data[0:1].to_dict(orient="records"))

    for idx in range(1, len(layer_config)):
        cur_col_idx = prev_col_idx + layer_config[idx][1]
        layer_config[idx].append(data[prev_col_idx:cur_col_idx].to_dict(orient="records"))
        prev_col_idx = cur_col_idx

    return layer_config


def download_avatar(avatar_url: str, placeholder_img: Path) -> Union[BytesIO, Path]:
    """Download the binary content off of the given URL and return a bytes buffer of the same.

    Parameters
    ----------
    avatar_url : str
        URL to download content/avatar from.
    placeholder_img : Path
        Image to use if no avatar URL is passed
        e.g. when the account is deleted

    Returns
    -------
    BytesIO | Path
        A bytes buffer of the downloaded content or
        the path to the placeholder image.
    """

    if avatar_url:
        r = requests.get(avatar_url, headers=COMMON_REQUEST_HEADERS)
        r.raise_for_status()
        return BytesIO(r.content)
    else:
        return placeholder_img


def create_mask(image: Image) -> Image:
    """Return a centered circular mask for any image.

    Parameters
    ----------
    image : Image
        Image to return the mask for.

    Returns
    -------
    Image
        Mask Image.
    """

    h, w = image.size
    mask_size = (h * 3, w * 3)
    alpha = Image.new("L", mask_size, 0)
    ImageDraw.Draw(alpha).pieslice([(0, 0), mask_size], 0, 360, fill=255)
    return alpha.resize(image.size, Image.LANCZOS)


def create_image_old(
    bg_size: tuple[int],
    bg_color: str,
    layer_config: LayerConfig,
    placeholder_img_path: Path = None,
    debug_img_path: Path = None,
) -> Image:

    bg = Image.new(mode="RGB", size=bg_size, color=bg_color)
    print("created background")

    print("creating circles. might take time...")

    for layer_idx in range(len(layer_config)):
        R, count, gap_size, users = layer_config[layer_idx]
        gaps_count = count - 1
        base_usr_img_angle = 360 / count
        # circumference = 2 * math.pi * R
        # usr_img_hw = math.floor(((circumference - (gaps_count * gap_size)) / count))

        # handle the central avatar size
        if layer_idx == 0:
            usr_img_hw = layer_config[1][0] + 40

        for user_idx in range(len(users)):

            if layer_idx != 0:
                # calc circumference according to nbr of holdings
                circumference = 2 * math.pi * R
                usr_img_hw = math.floor(((circumference - (gaps_count * gap_size)) / count))

            if debug_img_path:
                avatar = Image.open(debug_img_path)
            else:
                avatar = Image.open(
                    #download_avatar(users[user_idx]["avatar_url"], placeholder_img_path)
                    download_avatar(users[user_idx]["avatar_url"], "res/placeholder_avatar.png")
                )

            avatar = avatar.convert("RGB").resize((usr_img_hw, usr_img_hw))

            angle = math.radians(base_usr_img_angle * user_idx + gap_size)

            # +center of the background image
            avatar_center_x = math.floor(math.cos(angle) * R + (bg.size[0] / 2))
            avatar_center_y = math.floor(math.sin(angle) * R + (bg.size[1] / 2))

            bg.paste(
                avatar,
                (
                    # Image.paste needs top left co-ordinates
                    # the avatar being a square, subtracting half of its height and width returns the top left co-ordinates
                    math.floor(avatar_center_x - (usr_img_hw / 2)),
                    math.floor(avatar_center_y - (usr_img_hw / 2)),
                ),
                create_mask(avatar),
            )

    return bg


from io import BytesIO

def create_image_new(
    bg_size: tuple[int],
    bg_color: str,
    layer_config: LayerConfig,
    placeholder_img_path: Path = None,
    debug_img_path: Path = None,
) -> BytesIO:

    bg = Image.new(mode="RGB", size=bg_size, color=bg_color)
    print("created background")

    print("creating circles. might take time...")

    for layer_idx in range(len(layer_config)):
        R, count, gap_size, users = layer_config[layer_idx]
        gaps_count = count - 1
        base_usr_img_angle = 360 / count

        if layer_idx == 0:
            usr_img_hw = layer_config[1][0] + 40

        for user_idx in range(len(users)):
            if layer_idx != 0:
                circumference = 2 * math.pi * R
                usr_img_hw = math.floor(((circumference - (gaps_count * gap_size)) / count))

            if debug_img_path:
                avatar = Image.open(debug_img_path)
            else:
                avatar = Image.open(
                    download_avatar(users[user_idx]["avatar_url"], "res/placeholder_avatar.png")
                )

            avatar = avatar.convert("RGB").resize((usr_img_hw, usr_img_hw))

            angle = math.radians(base_usr_img_angle * user_idx + gap_size)

            avatar_center_x = math.floor(math.cos(angle) * R + (bg.size[0] / 2))
            avatar_center_y = math.floor(math.sin(angle) * R + (bg.size[1] / 2))

            bg.paste(
                avatar,
                (
                    math.floor(avatar_center_x - (usr_img_hw / 2)),
                    math.floor(avatar_center_y - (usr_img_hw / 2)),
                ),
                create_mask(avatar),
            )

    # Save the image to a BytesIO object
    image_bytes = BytesIO()
    bg.save(image_bytes, format='PNG')

    return image_bytes