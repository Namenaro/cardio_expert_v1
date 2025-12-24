import math

def get_test_and_train_ids(LUDB_data):
    patients_ids=list(LUDB_data.keys())
    # 70 % трейн, 30% тест
    num_train = math.ceil(len(patients_ids) * 0.7)
    train_ids = patients_ids[0:num_train]
    test_ids = patients_ids[num_train:]
    return train_ids, test_ids


if __name__ == "__main__":
    from paths import PATH_TO_LUDB
    import json
    from pathlib import Path

    # Откроем датасет LUDB
    path_to_dataset = Path(PATH_TO_LUDB)
    with open(path_to_dataset, 'r') as file:
        LUDB_data = json.load(file)

    # Получим id-шники тестовых и трейновых пациентов
    train_ids, test_ids = get_test_and_train_ids(LUDB_data=LUDB_data)

    # Распечатаем размеры теста и трейна
    print("train: " + str(len(train_ids)))
    print("test: " + str(len(test_ids)))