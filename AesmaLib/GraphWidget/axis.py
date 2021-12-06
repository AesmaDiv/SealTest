"""
# AesmaDiv 02.2020
# Класс для графиков. Параметры оси.
# Расчёт максимального и минимального значений по оси,
# количества делений и цены делений
"""
import math
from AesmaLib.GraphWidget.axis_params import AxisParams


class Axis:
    """ Класс оси """
    def __init__(self, axis_min: float = 0.0, axis_max: float = 0.0):
        keys = ['axis_min', 'axis_max', 'length', 'divs', 'price']
        self._params = dict.fromkeys(keys)
        self._divs_manually_set = False
        # если аргуметы переданы - расчет параметров оси
        if any((axis_min, axis_max)):
            self.calculate(axis_min, axis_max)

    def setMinimum(self, axis_min: float):
        """ установить минимальный предел оси """
        if self.getMaximum() > axis_min:
            self._params.update({'axis_min': axis_min})
            self.calculate(self.getMinimum(), self.getMaximum())

    def getMinimum(self):
        """ минимальный предел оси """
        return self._params['axis_min']

    def setMaximum(self, axis_max: float):
        """ установить максмальный предел оси """
        if self.getMinimum() < axis_max:
            self._params.update({'axis_max': axis_max})
            self.calculate(self.getMinimum(), self.getMaximum())

    def getMaximum(self):
        """ максимальный предел оси """
        return self._params['axis_max']

    def getLength(self):
        """ полная длина оси """
        return abs(self._params['axis_max'] - self._params['axis_min'])

    def setDivs(self, divs: int):
        """ задать количество делений на оси """
        divs = abs(divs) # должно быть положительное
        self._divs_manually_set = divs > 0
        self._params.update({'divs': divs})
        self.calculate(self.getMinimum(), self.getMaximum())

    def getDivs(self):
        """ количество делений на оси """
        return int(self._params['divs'])

    def getPrice(self):
        """ цена деления """
        return self._params['price']

    def generateDivSteps(self):
        """ генератор значений делений """
        for i in range(self.getDivs() + 1):
            result = float(i) * self._params['price'] + self._params['axis_min']
            yield i, result

    def calculate(self, axis_min: float, axis_max: float):
        """ расчёт параматров """
        params = AxisParams.calculate(axis_min, axis_max)
        self._params['axis_min'] = params['min']
        self._params['axis_max'] = params['max']
        self._params['length'] = params['len']
        self._params['divs'] = params['div']
        self._params['price'] = params['prc']
