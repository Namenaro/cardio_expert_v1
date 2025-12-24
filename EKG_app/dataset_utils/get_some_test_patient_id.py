from paths import PATH_TO_LUDB

import json
from pathlib import Path

def get_some_test_patient_id():
    # Откроем датасет LUDB
    path_to_dataset = Path(PATH_TO_LUDB)
    with open(path_to_dataset, 'r') as file:
        LUDB_data = json.load(file)

    # возьмем id-шник i-того  пациента датасета
    i = 1
    patient_ids = list(LUDB_data.keys())
    patient_id = patient_ids[i]
    return patient_id

if __name__ == "__main__":
    print(get_some_test_patient_id())