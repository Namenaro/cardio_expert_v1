from pathlib import Path
import json
import os

from CORE.datasets_wrappers.third_party_dataset import ThirdPartyDataset
from CORE.paths import DB_PATH, EXEMPLARS_DATASETS_PATH


class FormDataset:
    def __init__(self, forms_dataset_name: str, outer_dataset: ThirdPartyDataset, ):
        full_path = os.path.join(EXEMPLARS_DATASETS_PATH, forms_dataset_name)


if __name__ == "__main__":
    from CORE.datasets_wrappers import LUDB

    ludb = LUDB()
    dataset = FormDataset(forms_dataset_name="test_form_dataset.json")
