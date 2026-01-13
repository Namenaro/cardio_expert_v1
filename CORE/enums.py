from enum import Enum
from types import SimpleNamespace


class CLASS_TYPES(Enum):
    PC = "PC"
    HC = "HC"
    PS = "PS"
    SM = "SM"


LEADS_NAMES = SimpleNamespace(
    i='i',
    ii='ii',
    iii='iii',
    avr='avr',
    avl='avl',
    avf='avf',
    v1='v1',
    v2='v2',
    v3='v3',
    v4='v4',
    v5='v5',
    v6='v6',
)
