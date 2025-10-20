from CORE.dataclasses import Form

from typing import List

class DBWrapperForDoctor:
    def __init__(self):
        pass

    def get_all_forms_names(self)->List[str]:
        #TODO
        return ["qr", "T", "P_hypertrophy_left", "ST_infarction"]

    def deserialize_form_by_name(self, form_name:str)->Form:
        pass

    def delete_form(self, form_name):
        pass

    def save_form(self, form:Form):
        pass


    # все остальные методы начинать с нижнего прочерка или вообще вынести из класса

    def _load_SM_class_info(self, class_name:str)->SMClassInfo:
        pass