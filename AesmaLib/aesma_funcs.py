"""
    Модуль вспомогательных функций для всякий операций
"""

def parseTo(to_type: type, string: str, default=None):
    """ Безопасная конвертация типов """
    try:
        return to_type(string)
    except (ValueError, TypeError):
        return default


def parseToFloat(string: str):
    """ Безопасная конвертация строки в число с пл.запятой """
    return parseTo(float, string, default=0.0)


def combineDicts(list_of_dicts: list):
    """ Объединение списка словарей """
    result = {}
    if list_of_dicts:
        for d in list_of_dicts:
            result |= d
    return result

def removeLesser(sorted_array: list, value, is_included=False):
    """ Удаляет из упорядоченого списка значения МЕНЬШЕ чем 'value'
        'is_included' - включительно
        возвращает новый список и индекс первого елемента
    """
    return removeFrom(sorted_array, value, '<', is_included)


def removeGreater(sorted_array: list, value, is_included=False):
    """ Удаляет из упорядоченого списка значения БОЛЬШЕ чем 'value'
        'is_included' - включительно
        возвращает новый список и индекс последнего елемента
    """
    return removeFrom(sorted_array, value, '>', is_included)


def removeFrom(sorted_array: list, value, condition='>', is_included=False):
    """ Удаляет из упорядоченого списка значения удовлетворяющие
        'condition':
            '>' - больше, чем 'value'
            '<' - меньше, чем 'value'
        'is_included' - включительно
        возвращает новый список и индекс последнего елемента
    """
    result = sorted_array.copy()
    index = getNext(result, value, is_included)
    if 0 < index < len(result):
        if condition == '>':
            del result[index:]
        else:
            del result[:index]
    return result, index


def getNext(sorted_array: list, value, is_including=False):
    """ Находит индекс первого элемента равного или больше value """
    if sorted_array:
        func = lambda x: x >= value if is_including else x > value
        try:
            result = next(i for i, v in enumerate(sorted_array) if func(v))
        except StopIteration:
            result = len(sorted_array)
    return result



def splitToSubarrays(array: list, elements_count: int, with_reminder=False):
    """ Разбивает список на части по 'elements_count' частей
        'with_reminder' - с остатком
    """
    result = []
    subarrays_count = len(array) // elements_count
    if with_reminder and len(array) % elements_count:
        subarrays_count += 1
    for i in range(subarrays_count):
        start = i * elements_count
        stop = start + elements_count
        result.append(array[start: stop])
    return result
