from CORE.pazzles_lib.SM_base import SM
from CORE.pazzles_lib.PS_base import PS

from typing import List

class Track:
    def __init__(self):
        self.SMs:List[SM] = []
        self.PSs: List[PS] = []

    def is_valid(self):
        return len(self.PSs) > 0