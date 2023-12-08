from enum import IntEnum, auto
from typing import Union

class Interaction(IntEnum):
    holdings = auto()

# [[layer radius, number of users in the layer, gap size, list of users in the layer], ...]
LayerConfig = list[list[Union[int, list[dict]]]]
