from typing import Optional, List

class Parameter:
    def __init__(self):
        self.name:str = ""
        self.comment:str = ""
        self.ordered_sample: List[float] = []
        self.weight_of_param_for_exemplar_evaluation: Optional[float] = None