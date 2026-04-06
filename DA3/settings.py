from dataclasses import dataclass
from typing import Type

from CORE.run.eval.base_eval import BaseEvaluator
from CORE.run.eval.positive_only import *


@dataclass
class Settings:
    max_half_padding_from_real_coord_of_first: float = 0.0005
    evaluator_class: Type[BaseEvaluator] = OneClassSVMEvaluator
