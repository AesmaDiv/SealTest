"""
    AesmaDiv 03.2020
    Класс для графиков: Данные графика.
    Точки и оси, функция трансляции значений по осям
    в координаты холста
"""
from typing import List
import math
import numpy as np
from scipy.interpolate import make_interp_spline
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt
from AesmaLib.GraphWidget.axis import Axis
from AesmaLib.journal import Journal


class ChartMeta:
    """ Класс болванка для класса графика"""
    def __init__(self, name: str = '', color: QColor = Qt.white,) -> None:
        self.name = name
        self.visibility = True
        self._pen = QPen(color, 1, style=Qt.SolidLine)
        self._axes = {}

    def setPen(self, pen: QPen, style=None):
        """ задание кисти """
        self._pen = pen
        if style:
            self._pen.setStyle(style)

    def getPen(self):
        """ получение кисти """
        return self._pen

    def setAxes(self, axes: dict):
        """ задание осей """
        self._axes = axes

    def getAxes(self):
        """ получение осей """
        return self._axes

    def setAxis(self, axis: Axis, name: str):
        """ задание оси по имени (x0, y0, y1 и тд)"""
        self._axes.update({name: axis})

    def getAxis(self, name: str):
        """ получение оси по имени """
        return self._axes[name] if name in self._axes.keys() else None


class Chart(ChartMeta):
    """ Класс кривой графика """
    def __init__(self, points: list = None, name: str = '',
                 color: QColor = Qt.white, options: str = ''):
        super().__init__(name=name, color=color)
        self._coefs = [1, 1]
        self._options = options
        self._ptype = np.dtype([('x', 'f4'),('y', 'f4')])
        self._points = self.createEmptyPoints()
        self._spline = None
        if points:
            self.setPoints(points, do_regenerate_axises=False)
            self._regenerateAxies()


    def setCoefs(self, coef_min: float, coef_max: float):
        """ задание коэфициентов """
        self._coefs = [coef_min, coef_max]

    def getCoefs(self):
        """ получение коэфициентов """
        return self._coefs

    def setOptions(self, options: str):
        """ задание опций """
        self._options = options

    def getOptions(self):
        """ получение опций """
        return self._options

    def setPoints(self, points: list, do_regenerate_axises: bool = True):
        """ задание точек """
        self._points = self.transposePoints(points)
        self._points.sort()
        if do_regenerate_axises:
            self._regenerateAxies()

    def getPoints(self, name: str = ''):
        """ получение списка точек """
        result = np.sort(self._points)
        if name in ('x', 'y'):
            return result[name]
        result = result.T
        return result.tolist()

    def addPoint(self, x: float, y: float, do_regenerate_axes: bool = False):
        """ добавление точки """
        point = np.array([(x, y)], dtype=self._ptype)
        self._points = np.concatenate((self._points, point))
        if do_regenerate_axes:
            self._regenerateAxies()
        if self._points.size > 2:
            self._regenerateSpline()

    def removePoint(self, index: int = -1, do_regenerate_axies: bool = False):
        """ удаление точки по индексу (по умолчанию последней)"""
        count = self._points.size
        if count and ((-1 * count) <= index < count):
            self._points = np.delete(self._points, index)
            if do_regenerate_axies:
                self._regenerateAxies()
        else:
            Journal.log(__name__, 'Error:: индекс вне диапазона')

    def clearPoints(self):
        """ удаление всех точек """
        self._points = self.createEmptyPoints()

    def createEmptyPoints(self):
        """ создание пустого массива точек """
        return np.empty(0, dtype=self._ptype)

    def getSpline(self):
        """ получение функции кривой """
        return self._spline

    def getTranslatedPoints(self, sz_canvas: List[float], for_curve=False):
        """ получение точек транслированных в коорд. пикселей """
        if for_curve and len(self._points['x']) > 2:
            points = self.regenerateCurve()
        else:
            points = np.sort(self._points)
        if points.size:
            coeff = 1
            func = lambda v: v * coeff
            for i, n in enumerate(('x', 'y')):
                coeff = sz_canvas[i] / self._axes[n].getLength()
                points[n] = list(map(func, points[n]))
        return points

    def translateCoordinate(self, name, value, length, to_pixel=True):
        """ трансляция значения относительно оси """
        if name in self._axes:
            # получение значения по оси из коорд.пикселя """
            if to_pixel:
                coef = length / self._axes[name].getLength()
                value = (value - self._axes[name].getMinimum()) * coef
            # получение коорд.пикселя из значение по оси
            else:
                coef = self._axes[name].getLength() / length
                value = self._axes[name].getMinimum() + value * coef
            return value
        Journal.log(__name__, "Error:: неверное имя оси")
        return 0

    def _regenerateAxies(self):
        """ перерасчёт осей """
        if self._points.size > 1:
            for name in ('x', 'y'):
                min_, max_ = min(self._points[name]), max(self._points[name])
                min_, max_, _ = Chart._calculateAxies(min_, max_)
                axis = Axis(min_ * 1.0, max_ * 1.0)
                self._axes.update({name: axis})
        self._regenerateSpline()

    def _regenerateSpline(self):
        """ перерасчёт функции кривой """
        if self._points.size > 2:
            points = np.sort(self._points)
            self._spline = make_interp_spline(points['x'], points['y'], k=2)
        else:
            self._spline = None

    def regenerateCurve(self, points=None, samples=100):
        """ перерасчёт точек кривой """
        if points is None and self._points.size > 2:
            return self.regenerateCurve(self._points)
        if self._spline:
            result_x = np.linspace(min(points['x']), max(points['x']), samples)
            result_y = self._spline(result_x)
            result = self.transposePoints([result_x, result_y])
            return result
        return self.createEmptyPoints()

    def transposePoints(self, points: list):
        """ транспонирование точек """
        if len(points) == 2 and len(points[0]):
            temp = np.array(points)
            temp = temp.T
            pnts = list(map(tuple, temp))
            result = np.array(pnts, dtype=self._ptype)
            return result
        Journal.log(__name__, 'Error:: массив координат имеет неверный формат')
        return self.createEmptyPoints()

    def _sortPoints(self):
        """ сортировка точек по первой координате """
        if len(self._points) > 1:
            self._points = sorted(self._points, key=lambda p: p[0])

    @staticmethod
    def _calculateAxies(axis_start, axis_end, ticks=10):
        """ расчёт удобного числа и значений делений оси """
        if axis_end - axis_start:
            nice_range = Chart._niceNumber(axis_end - axis_start, 0)
            nice_tick = Chart._niceNumber(nice_range / (ticks - 1), 1)
            new_axis_start = math.floor(axis_start / nice_tick) * nice_tick
            new_axis_end = math.ceil(axis_end / nice_tick) * nice_tick
            axis_start = new_axis_start
            axis_end = new_axis_end
            return (new_axis_start, new_axis_end, nice_tick)
        return (axis_start, axis_end, ticks)

    @staticmethod
    def _niceNumber(value, round_=False):
        '''nice_number(value, round_=False) -> float'''
        exponent = math.floor(math.log(value, 10))
        fraction = value / 10 ** exponent
        if round_:
            if fraction < 1.5:
                nice_fraction = 1.
            elif fraction < 3.:
                nice_fraction = 2.
            elif fraction < 7.:
                nice_fraction = 5.
            else:
                nice_fraction = 10.
        else:
            if fraction <= 1:
                nice_fraction = 1.
            elif fraction <= 2:
                nice_fraction = 2.
            elif fraction <= 5:
                nice_fraction = 5.
            else:
                nice_fraction = 10.
        return nice_fraction * 10 ** exponent

    @staticmethod
    def _niceBounds(axis_start, axis_end, num_ticks=10):
        '''
        nice_bounds(axis_start, axis_end, num_ticks=10) -> tuple
        @return: tuple as (nice_axis_start, nice_axis_end, nice_tick_width)
        '''
        axis_width = axis_end - axis_start
        nice_tick = 0
        if axis_width:
            nice_range = Chart._niceNumber(axis_width)
            nice_tick = Chart._niceNumber(nice_range / (num_ticks - 1), True)
            axis_start = math.floor(axis_start / nice_tick) * nice_tick
            axis_end = math.ceil(axis_end / nice_tick) * nice_tick
        return axis_start, axis_end, nice_tick
