from settings import LEADS_NAMES, LEADS_NAMES_ORDERED

def get_signal_by_id_and_lead_mkV(patient_id, lead_name, LUDB_data):
    signal_mkV = LUDB_data[patient_id]['Leads'][lead_name]['Signal']
    return signal_mkV

def get_signal_by_id_and_lead_mV(patient_id, lead_name, LUDB_data):
    signal_mkV = get_signal_by_id_and_lead_mkV(patient_id, lead_name, LUDB_data)
    signal_mV = [s / 1000 for s in signal_mkV]  # делим на 1000, т.к. хотим в мВ, а в датасете сигнал записан в мкВ
    return signal_mV

def get_all_signals_by_id_mkV(patient_id, LUDB_data):
    """ Сигнал данного пациента со всемх отведений, упорядоченных стандарнтым образом, в микро_вотльтах. """
    signals_list, lead_names_list = get_signals_by_id_several_leads_mkV(patient_id, LUDB_data, leads_names_list=LEADS_NAMES_ORDERED)
    return signals_list, lead_names_list

def get_signals_by_id_several_leads_mkV(patient_id, LUDB_data, leads_names_list):
    """ Cигнал данного пациента с некоторых отведений, в микро_вотльтах. """
    signals_list = []
    for lead_name in leads_names_list:
        lead_signal =  get_signal_by_id_and_lead_mkV(patient_id, lead_name, LUDB_data)
        signals_list.append(lead_signal)
    return signals_list, leads_names_list

def get_signals_by_id_several_leads_mV(patient_id, LUDB_data, leads_names_list):
    """ Cигнал данного пациента с некоторых отведений, в микро_вотльтах. """
    signals_list = []
    for lead_name in leads_names_list:
        lead_signal =  get_signal_by_id_and_lead_mkV(patient_id, lead_name, LUDB_data)
        lead_signal = [s / 1000 for s in lead_signal]  # делим на 1000, т.к. хотим в мВ, а в датасете в мкВ
        signals_list.append(lead_signal)
    return signals_list, leads_names_list


if __name__ == "__main__":
    from get_some_test_patient_id import get_some_test_patient_id
    from get_LUDB_data import get_LUDB_data

    patient_id = get_some_test_patient_id()
    lead_name = LEADS_NAMES.v4
    LUDB_data = get_LUDB_data()

    # сигнал данного пациента в милливотльтах в данном отведении
    signal_one_lead = get_signal_by_id_and_lead_mV(patient_id, lead_name, LUDB_data)
    print(signal_one_lead)

    # сигнал данного пациента в микро_вотльтах в данном отведении
    signal_one_lead = get_signal_by_id_and_lead_mkV(patient_id, lead_name, LUDB_data)
    print(signal_one_lead)


    print('сигнал данного пациента со всемх отведений, упорядоченных стандарнтым образом, в микро_вотльтах:')
    signals_list, lead_names_list = get_all_signals_by_id_mkV(patient_id, LUDB_data)
    print(len(signals_list))
    print(lead_names_list)


    print('сигнал данного пациента с избранных отведений,  в микро_вотльтах:')
    signals_list, lead_names_list = get_signals_by_id_several_leads_mkV(patient_id, LUDB_data, leads_names_list=[LEADS_NAMES.i, LEADS_NAMES.avf])
    print(len(signals_list))
    print(lead_names_list)