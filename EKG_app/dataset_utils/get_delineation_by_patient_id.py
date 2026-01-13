from settings import LEADS_NAMES, POINTS_TYPES, WAVES_TYPES, FREQUENCY

def get_one_lead_delineation_by_patient_id(patient_id, LUDB_data, lead_name=LEADS_NAMES.iii, point_type=POINTS_TYPES.P_START):
    """ Для данного пациента получить координаты точек такого-то типа в таком-то отведении. """
    result_coords = []

    wave = None
    if point_type in [POINTS_TYPES.QRS_PEAK, POINTS_TYPES.QRS_END, POINTS_TYPES.QRS_START]:
        wave = WAVES_TYPES.QRS
    else:
        if point_type in [POINTS_TYPES.T_PEAK, POINTS_TYPES.T_END, POINTS_TYPES.T_START]:
            wave = WAVES_TYPES.T
        else:
            if point_type in [POINTS_TYPES.P_PEAK, POINTS_TYPES.P_END, POINTS_TYPES.P_START]:
                wave = WAVES_TYPES.P

    id_in_triplet = None
    if point_type in [POINTS_TYPES.QRS_PEAK, POINTS_TYPES.T_PEAK, POINTS_TYPES.P_PEAK]:
        id_in_triplet=1
    else:
        if point_type in [POINTS_TYPES.QRS_START, POINTS_TYPES.T_START, POINTS_TYPES.P_START]:
            id_in_triplet = 0
        else:
            if point_type in [POINTS_TYPES.QRS_END, POINTS_TYPES.T_END, POINTS_TYPES.P_END]:
                id_in_triplet = 2

    points_triplets = LUDB_data[patient_id]['Leads'][lead_name]['Delineation'][wave]
    for triplet in points_triplets:
        result_coords.append(triplet[id_in_triplet])

    result_coords = list([result_coords[i] / FREQUENCY for i in range(len(result_coords))])
    return result_coords

def get_full_wave_delineation_by_patient_id(patient_id,  LUDB_data, lead_name=LEADS_NAMES.i, wave=WAVES_TYPES.QRS):
    # Возвразает список троек координат в конкретном отведении данного раицента.
    # Каждая тройка соотв. [начало, пик, конец] волны заданного типа (например, QRS)
    triplets  = LUDB_data[patient_id]['Leads'][lead_name]['Delineation'][wave]
    triplets = [[triplets[i][0]/ FREQUENCY, triplets[i][1]/ FREQUENCY, triplets[i][2]/ FREQUENCY] for i in range(len(triplets))]
    return triplets

if __name__ == "__main__":
    from get_LUDB_data import get_LUDB_data
    from get_some_test_patient_id import get_some_test_patient_id

    LUDB_data = get_LUDB_data()
    patient_id =  get_some_test_patient_id()

    # координаты точек такого-то конкретного типа (например, пик QRS) в конкретном отведении данного паицента:
    points_delineation = get_one_lead_delineation_by_patient_id(patient_id, LUDB_data, lead_name=LEADS_NAMES.i, point_type=POINTS_TYPES.QRS_PEAK)
    print(points_delineation)

    # координаты точек целых волн (например, комплекса QRS) в конкретном отведении данного паицента:
    wave_delineation = get_full_wave_delineation_by_patient_id(patient_id,  LUDB_data, lead_name=LEADS_NAMES.i, wave=WAVES_TYPES.QRS)
    print(wave_delineation)
