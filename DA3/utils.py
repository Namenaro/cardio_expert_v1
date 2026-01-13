from CORE.db_dataclasses import *


def get_affected_form_parameters(puzzle: BasePazzle, form_parameters: List[Parameter]) -> List[str]:
    """
    Получить список имен параметров формы, которые упоминаются как входные параметры пазла
    :param puzzle: рассматриваемый пазл произвольного типа
    :param form_parameters: список параметров формы, к которой привязан этот пазл
    :return: список имен параметров
    """
    if not hasattr(puzzle, 'input_param_values') or not puzzle.input_param_values:
        return []

    # Собираем ID параметров формы из input_param_values
    param_ids = []
    for param_value in puzzle.input_param_values:
        if (isinstance(param_value, ObjectInputParamValue) and hasattr(param_value,
                                                                       'parameter_id') and param_value.parameter_id is not None):
            param_ids.append(param_value.parameter_id)

    if not param_ids:
        return []

    # Ищем имена параметров в списке form_parameters
    param_names = []
    for param_id in param_ids:
        # Ищем параметр по ID
        found_param = None
        for param in form_parameters:
            if param.id == param_id:
                found_param = param
                break

        if found_param and found_param.name:
            param_names.append(found_param.name)
        else:
            param_names.append(f"ID:{param_id}")

    return param_names
