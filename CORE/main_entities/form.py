from .step import Step

from typing import List

class Form:
    def __init__(self):
        self.name: str = ""
        self.comment: str = ""
        self.steps_list: List[Step] = []

