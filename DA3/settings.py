from dataclasses import dataclass


@dataclass
class Settings:
    max_half_padding_from_real_coord_of_first: float = 0.05
