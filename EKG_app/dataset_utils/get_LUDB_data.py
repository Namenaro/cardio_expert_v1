from paths import PATH_TO_LUDB
import json
from pathlib import Path

def get_LUDB_data():
    path_to_dataset = Path(PATH_TO_LUDB)
    with open(path_to_dataset, 'r') as file:
        LUDB_data = json.load(file)
        return LUDB_data
    return None


if __name__ == "__main__":
    LUDB_data = get_LUDB_data()
    print ("Записей в датасете: " + str(len(LUDB_data)))