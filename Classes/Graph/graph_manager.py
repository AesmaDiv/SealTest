"""
    Модуль содержит функции работы с графиками
"""
from PyQt5.QtGui import QPalette, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QFrame
from Classes.Graph.pump_graph import PumpGraph
from Classes.Graph.graph_markers import Markers
from Classes.UI.funcs_aux import calculateEffs
from AesmaLib.GraphWidget.chart import Chart
from AesmaLib.journal import Journal


class GraphManager(PumpGraph):
    """ Менеджер графиков """
    def __init__(self, testdata) -> None:
        super().__init__(100, 100, parent=None)
        self._testdata = testdata
        self._markers = None
        self.setMargins([10, 10, 10, 10])

    def initMarkers(self, params, host):
        """ инициализация маркеров """
        self._markers = Markers(params.keys(), self)
        for key, val in params.items():
            self._markers.setMarkerColor(key, val)
        host.addWidget(self._markers, 0, 0)

    def drawCharts(self, frame: QFrame):
        """ отрисовка графиков испытания """
        self.clearCharts()
        if self._testdata.type_:
            charts = self._loadCharts()
            for chart in charts.values():
                self.addChart(chart, chart.name)
            self.setLimits(self._testdata.type_['Min'],
                            self._testdata.type_['Nom'],
                            self._testdata.type_['Max'])
        self.displayCharts(frame)

    def displayCharts(self, frame: QFrame):
        """ вывод графика в рисунок и в frame """
        pic = self.renderToImage(frame.size())
        palette = frame.palette()
        palette.setBrush(QPalette.Background, QBrush(pic))
        frame.setPalette(palette)
        frame.setAutoFillBackground(True)

    def _loadCharts(self):
        """ загрузка данных о точках """
        points = self._getPoints('etalon')
        result = self.createCharts_etalon(points)
        if self._testdata.test_:
            points = self._getPoints('test')
            result.update(self.createCharts_test(points, result))
        return result

    def _getPoints(self, chart_type='etalon'):
        """ парсинг значений точек из строк """
        is_etalon = (chart_type == 'etalon')
        src = self._testdata.type_ if is_etalon else self._testdata.test_
        if src.num_points:
            flws = src.values_flw
            lfts = src.values_lft
            pwrs = src.values_pwr
            if is_etalon:
                pwrs = list(map(lambda x: x * 0.7457, pwrs))
            effs = calculateEffs(flws, lfts, pwrs)
            return [flws, lfts, pwrs, effs]
        return None

    def createCharts_etalon(self, points: list):
        """ создание кривых графиков для эталона """
        result = {}
        if points:
            ch_lft = self._createChart(points[0], points[1], 'lft', 'limits')
            ch_pwr = self._createChart(points[0], points[2], 'pwr', 'limits')
            ch_eff = self._createChart(points[0], points[3], 'eff', '')
            ch_lft.setPen(QPen(QColor(200, 200, 255), 1), Qt.DashLine)
            ch_pwr.setPen(QPen(QColor(255, 0, 0), 1), Qt.DashLine)
            ch_eff.setPen(QPen(QColor(0, 255, 0), 1), Qt.DashLine)
            self._scaleChart(ch_lft, (0.95, 1.1), 0, 0)
            self._scaleChart(ch_pwr, (0.95, 1.1), 0, ch_lft.getAxis('y').getDivs())
            self._scaleChart(ch_eff, (1.0, 1.0),  0, ch_lft.getAxis('y').getDivs())
            result.update({'lft': ch_lft,
                        'pwr': ch_pwr,
                        'eff': ch_eff})
        return result

    def createCharts_test(self, points: list, etalon_charts: dict):
        """ создание кривых графиков для проведённого испытания """
        result = {}
        if points and len(etalon_charts) == 3:
            ch_lft = self._createChart(points[0], points[1], 'test_lft', 'knots')
            ch_pwr = self._createChart(points[0], points[2], 'test_pwr', 'knots')
            ch_eff = self._createChart(points[0], points[3], 'test_eff', 'knots')
            ch_lft.setPen(QPen(etalon_charts['lft'].getPen()), Qt.SolidLine)
            ch_pwr.setPen(QPen(etalon_charts['pwr'].getPen()), Qt.SolidLine)
            ch_eff.setPen(QPen(etalon_charts['eff'].getPen()), Qt.SolidLine)
            self._scaleChart(ch_lft, axes=etalon_charts['lft'].getAxes())
            self._scaleChart(ch_pwr, axes=etalon_charts['pwr'].getAxes())
            self._scaleChart(ch_eff, axes=etalon_charts['eff'].getAxes())
            result.update({'test_lft': ch_lft,
                        'test_pwr': ch_pwr,
                        'test_eff': ch_eff})
        return result

    @staticmethod
    def _createChart(coords_x: list, coords_y: list, name: str, options=''):
        """ создание и настройка экземпляра класса кривой """
        # points = [QPointF(x, y) for x, y in zip(coords_x, coords_y)]
        # result = Chart(points, name, options=options)
        result = Chart([coords_x.copy(), coords_y.copy()], name, options=options)
        return result

    @staticmethod
    def _scaleChart(chart: Chart, coefs=(1.0, 1.0), ymin=0, yticks=0, axes=None):
        """ установка размерности для осей и области допуска """
        chart.setCoefs(*coefs)
        if axes:
            chart.setAxes(axes)
        else:
            chart.getAxis('y').setMinimum(ymin)
            if yticks:
                chart.getAxis('y').setDivs(yticks)

    def saveTestdata(self):
        """ сохранение данных из таблицы в запись испытания """
        points_lft_x = super().getChart('test_lft').getPoints('x')
        points_lft_y = super().getChart('test_lft').getPoints('y')
        # points_pwr_x = super().get_chart('test_pwr').getPoints('x')
        points_pwr_y = super().getChart('test_pwr').getPoints('y')
        self._testdata.test_['Flows'] = ','.join(list(map(str, points_lft_x)))
        self._testdata.test_['Lifts'] = ','.join(list(map(str, points_lft_y)))
        self._testdata.test_['Powers'] = ','.join(list(map(str, points_pwr_y)))

    def markersReposition(self):
        """ перенос маркеров на другой холст """
        self._markers.repositionFor(self)

    def markersMove(self, params):
        """ перемещение маркеров отображающих текущие значения """
        for param in params:
            self._markers.moveMarker(
                QPointF(param['x'], param['y']),
                param['name']
            )

    def markersAddKnots(self):
        """ добавление узлов (точки) """
        self._markers.addKnots()

    def markersRemoveKnots(self):
        """ удаление узлов (точки) """
        self._markers.removeKnots()

    def markersClearKnots(self):
        """ очистка узлов (всех точек) """
        self._markers.clearAllKnots()

    def setPointLines_max(self, value):
        """ установка макс.значения расхода для линий отбивания точек """
        self._markers.setPointLinesMax(value)

    def setPointLines_num(self, value):
        """ установка кол-ва линий для отбивания точек """
        self._markers.setPointLinesNumber(value)
        self._markers.repaint()

    def setPointLines_cur(self, value):
        """ установка кол-ва линий для отбивания точек """
        self._markers.setPointLinesCurrent(value)
        self._markers.repaint()

    def checkPointExists(self, flw) -> bool:
        """ проверка есть ли точка с таким значением по Х """
        chart: Chart = super().getChart('test_lft')
        points = chart.getPoints('x')
        return flw in points

    def addPointsToCharts(self, flw, lft, pwr, eff):
        """ добавление точек напора и мощности на график """
        self._addPointToChart('test_lft', flw, lft)
        self._addPointToChart('test_pwr', flw, pwr)
        self._addPointToChart('test_eff', flw, eff)

    def _addPointToChart(self, chart_name: str, value_x: float, value_y: float):
        """ добавление точки на график """
        chart: Chart = super().getChart(chart_name)
        if chart is not None:
            Journal.log(__name__, '\tдобавление точки к графику', value_x, value_y)
            chart.addPoint(value_x, value_y)
        else:
            Journal.log(__name__, '\tError: нет такой кривой', chart_name)
            etalon: Chart = super().getChart(chart_name.replace('test_', ''))
            if etalon is not None:
                chart: Chart = Chart(name=chart_name)
                chart.setAxes(etalon.getAxes())
                chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
                self.addChart(chart, chart_name)
                self._addPointToChart(chart_name, value_x, value_y)
            else:
                Journal.log(__name__, '\tError: не найден эталон для', chart_name)

    def _getChart(self, name: str):
        """ получение ссылки на кривую по имени """
        chart_name = name
        chart: Chart = super().getChart(chart_name)
        if chart is None:
            etalon: Chart = super().getChart(chart_name.replace('test_', ''))
            if etalon is not None:
                chart: Chart = Chart(name=chart_name)
                chart.setAxes(etalon.getAxes())
                chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
                self.addChart(chart, chart_name)
            else:
                Journal.log(__name__, 'Error: не найден эталон для', chart_name)
        return chart

    def clearPointsFromCharts(self):
        """ удаление всех точек из графиков напора и мощности """
        self._clearPointsFromChart('test_lft')
        self._clearPointsFromChart('test_pwr')
        self._clearPointsFromChart('test_eff')

    def _clearPointsFromChart(self, chart_name: str):
        """ удаление всех точек из графика """
        chart = super().getChart(chart_name)
        if chart is not None:
            chart.clearPoints()

    def removeLastPointsFromCharts(self):
        """ удаление последних точек из графиков напора и мощности """
        self._removeLastPointFromChart('test_lft')
        self._removeLastPointFromChart('test_pwr')
        self._removeLastPointFromChart('test_eff')

    def _removeLastPointFromChart(self, chart_name: str):
        """ удаление последней точки из графика """
        chart = super().getChart(chart_name)
        if chart is not None:
            chart.removePoint()

    def switchChartsVisibility(self, state):
        """ переключение видимости для кривых """
        # если включено - показывать все графики
        # если выключено - только тестовые (напор / мощность)
        self.setVisibleCharts(['lft', 'pwr', 'test_lft', 'test_pwr']
                                            if not state else 'all')
        # переключение видимости линий для отбивания точек
        # если выключена видимость всех - показывается линии
        self._markers.setPointLinesVis(not state)
        self.displayCharts(self._markers)

    def generateResultText(self):
        """ генерирует миниотчёт об испытании """
        self._testdata.dlts_.clear()
        result_lines = []
        # if self._testdata.test_['Flows']:
        self._generateDeltasReport(result_lines)
        self._generateDeltaEffsReport(result_lines)
        return '\n'.join(result_lines)

    def _generateDeltasReport(self, lines: list):
        """ расчитывает отклонения для напора и мощности """
        for name, title in zip(('lft', 'pwr'),('Напор', 'Мощность')):
            self._calculateDeltasFor(name)
            string = f'\u0394 {title}, %\t'
            for val in self._testdata.dlts_[name]:
                frmt = '{:>10.2f}' if val else '-.--'
                string += f'\t{frmt}'.format(val)
            lines.append(string)

    def _generateDeltaEffsReport(self, lines: list):
        """ расчитывает отклонения для кпд """
        result = None
        chart = self._getChart('test_eff')
        spline = chart.getSpline()
        if spline:
            curve = chart.regenerateCurve()
            nom = self._testdata.type_['Nom']
            eff_nom = float(spline(nom))
            eff_max = float(max(curve['y']))
            result = abs(eff_max - eff_nom)
        frmt = '{:>10.2f}' if result else '-.--'
        string = f'Отклонение КПД от номинального, %\t{frmt}'.format(result)
        lines.append(string)
        self._testdata.dlts_['eff'] = result

    def _calculateDeltasFor(self, chart_name: str):
        """ расчитывает отклонения для указанной характеристики """
        names = (f'test_{chart_name}', f'{chart_name}')
        ranges = ('Min', 'Nom', 'Max')
        get_val = lambda spl, rng: float(spl(self._testdata.type_[rng]))
        get_dlt = lambda tst, etl: round((tst / etl * 100 - 100), 2)
        vals, result = [], [None] * 3
        for name in names:
            spln = self._getChart(f'{name}').getSpline()
            if spln:
                vals.append([get_val(spln, rng) for rng in ranges])
        if len(vals) > 1:
            result = [get_dlt(x, y) for x, y in zip(vals[0], vals[1])]
        self._testdata.dlts_[name] = result
