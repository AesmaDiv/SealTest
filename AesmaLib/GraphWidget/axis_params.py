"""
    Модуль содержит класс, для расчёта параметров оси:
    мин.значение, макс.значение, кол-во делений, цена деления, общая длина
"""
class AxisParams:
    """ Класс расчёта параметров оси """
    DIVIDERS = (10,8,7,6,5,4)   # допустимые делители
    _params = {                 # параметры оси
        'min': 0.0,             # мин.значение
        'max': 1.0,             # макс.значение
        'div': 1,               # кол-во делений
        'prc': 1.0,             # цена деления
        'len': 1                # общая длина
    }

    @staticmethod
    def calculate(v0: float, v1: float):
        """ расчёт параметров оси """
        params = AxisParams._params
        # расчет длины строкового представления числа, для длины округления
        params['len'] = max(map(len, (str(v0), str(v1))))
        # определение большой и малой полуосей
        params['min'] = v0 if abs(v0) < abs(v1) else v1
        params['max'] = v0 if abs(v0) > abs(v1) else v1
        # расчёт
        AxisParams._calculateMax()
        if all((v0, v1)):
            AxisParams._calculateMin()
        AxisParams._normalize()
        return params

    @staticmethod
    def _calculateMax():
        """ расчет параметров большой полуоси """
        params = AxisParams._params
        # для расчёта нужны первые две значимые цифры из числа,
        # т.е. 0.0123 -> 12, 456.78 -> 45
        # поэтому переводим число к экспоненциальному виду
        # и получаем эти две цифры и экспоненту
        sval = "{0:.1e}".format(params['max'])
        val, exp = list(map(float, sval.split('e')))
        val, exp = val * 10, exp - 1
        # ищем подходящий делитель
        divider = 0
        while not divider:
            val += -1 * (val < 0) + (val > 0)
            divider = next(filter(lambda x: val % x == 0, AxisParams.DIVIDERS), 0)
        # когда делитель найден, сохраняем параметры
        if divider:
            params['max'] = round(val * 10 ** exp, params['len'])
            params['div'] = int(divider)
            params['prc'] = abs(round(params['max'] / divider, params['len']))

    @staticmethod
    def _calculateMin():
        """ расчёт параметров малой полуоси """
        params = AxisParams._params
        sign_min = -1 if params['min'] < 0 else 1
        sign_max = -1 if params['max'] < 0 else 1
        # расчёт кол-ва делений
        divider = int(abs(params['min']) // params['prc'])
        # если оба значения на одной стороне полуоси..
        if sign_min == sign_max:
            params['div'] -= divider
        # если на разных..
        else:
            divider += 1
            params['div'] += divider
        params['min'] = round(params['prc'] * divider * sign_min, params['len'])

    @staticmethod
    def _normalize():
        """ нормализация """
        params = AxisParams._params
        # правильный порядок большего и меньшего края оси
        if params['min'] > params['max']:
            params['min'], params['max'] = params['max'], params['min']
        # полная длина оси
        params['len'] = params['max'] - params['min']

if __name__ == "__main__":
    axes = [
        (-2.2, -1.1),
        (-1.1, -2.2),
        (-1.1, 2.2),
        (1.1, 2.1),
        (0, 0.0123),
        (-0.0123, 0),
        (23.345, 45.678),
        (1023.12, 1245.56)
    ]
    func = lambda x, y, r: round(x['min'] + y * x['prc'], r)
    for axis in axes:
        prms = AxisParams.calculate(*axis)
        print(f"{axis}\n{prms}")
        str_len = max(map(len, (str(prms['min']), str(prms['max']))))
        print([func(prms, x, str_len) for x in range(prms['div'] + 1)])
