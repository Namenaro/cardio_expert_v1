

def map_names_to_values_throught_id(ids_to_names, ids_to_vals):
    # Проверяем, что оба словаря по одному ключу
    names_keys = set(ids_to_names.keys())
    vals_keys = set(ids_to_vals.keys())

    if names_keys != vals_keys:
        missing_in_vals = names_keys - vals_keys
        missing_in_names = vals_keys - names_keys

        if missing_in_vals:
            raise ValueError(f"Отсутствуют ключи в ids_to_vals: {missing_in_vals}")
        if missing_in_names:
            raise ValueError(f"Отсутствуют ключи в ids_to_names: {missing_in_names}")

    # Проверяем, что все значения в ids_to_names уникальны
    names_values = list(ids_to_names.values())
    if len(names_values) != len(set(names_values)):
        raise ValueError(f"Дубли среди имен в ids_to_names")

    names_to_vals = {
        ids_to_names[key]: ids_to_vals[key]
        for key in ids_to_names
    }
    return names_to_vals