"""
    Модуль содержит описание класса виджета графика
    испытания ЭЦН
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt5.QtGui import QFont, QFontMetricsF, QTransform
from PyQt5.QtCore import QPointF, Qt, QRectF, QSizeF
from AesmaLib.GraphWidget.axis import Axis
from AesmaLib.GraphWidget.chart import Chart
from AesmaLib.GraphWidget import funcs_spline as SplineFuncs
from AesmaLib.journal import Journal

is_logged = True
is_updated = False


class Graph(QWidget):
    """ Класс виджета графика """
    def __init__(self, width=400, height=300, parent=None):
        QWidget.__init__(self, parent)
        self.setGeometry(0, 0, width, height)
        self._margins = [20, 20, 40, 50]
        self._charts: dict = {}     # кривые
        self._base_chart = 'none'   # кривая определяющая размерность осей
        self._divs_x = 1            # кол-во делений оси X
        self._divs_y = 1            # кол-во делений оси Y
        self._style = {
            'background': QBrush(QColor(30, 30, 30)),
            'grid': {
                'backgound': QBrush(QColor(50, 50, 50)),
                'pen': QBrush(QColor(50, 50, 50)),
                'border': QPen(QColor(255, 255, 255), 2),
                'font': QFont("times", 10)
            }
        }

    def setMargins(self, margins: list):
        """ установка списка отступов """
        if len(margins) == 4:
            self._margins = margins
        else:
            if is_logged:
                Journal.log(__name__, '\tError:: margins len incorrect')

    def getMargins(self):
        """ получение ссылки на список отступов """
        return self._margins

    def getDrawArea(self):
        """ получение размеров области отрисовки графиков """
        return QRectF(self._margins[0], self._margins[1],
                      self.width() - self._margins[0] - self._margins[2],
                      self.height() - self._margins[1] - self._margins[3])

    def addChart(self, chart: Chart, name: str):
        """ добавление кривой по имени """
        if is_logged:
            Journal.log(__name__, "\tadding chart", name)
        self._charts.update({name: chart})
        self._updateBaseChart(chart, name)

    def removeChart(self, name: str):
        """ удаление кривой по имени """
        if name in self._charts.keys():
            if is_logged:
                Journal.log(__name__, "\tremoving chart", name)
            del self._charts[name]
            if self._base_chart == name:
                self._updateBaseChart(None, 'none')

    def replaceChart(self, chart: Chart, name: str):
        """ замена кривой по имени """
        if name in self._charts.keys():
            if is_logged:
                Journal.log(__name__, "\treplacing chart", name)
            self._charts.update({name: chart})
            if self._base_chart == name:
                self._updateBaseChart(chart, name)

    def clearCharts(self):
        """ удаление всех кривых """
        if is_logged:
            Journal.log(__name__, "\tclearing charts")
        self._charts.clear()
        self._updateBaseChart(None, 'none')

    def paintEvent(self, _event):
        """ событие перерисовки компонента """
        if is_logged:
            Journal.log(__name__, "\tpaintEvent -> begin *************")
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing, True)
        self._drawGrid(painter)
        self._drawCharts(painter)
        self._drawBorder(painter)
        painter.end()
        if is_logged:
            Journal.log(__name__, "\tpaintEvent -> end *************")

    def _drawGrid(self, painter: QPainter):
        """ отрисовка сетки графика """
        if len(self._charts):
            if is_logged:
                Journal.log(__name__, "\tdrawGrid ->")
            step_x, step_y = self._getSteps()
            pen = painter.pen()
            painter.setPen(self._style['grid']['pen'])
            self._drawGridBackground(painter)
            self._drawGridLines_x(painter, step_x)
            self._drawGridLines_y(painter, step_y)
            self._drawGridDivs_y(painter, step_y)
            self._drawGridDivs_x(painter, step_x)
            painter.setPen(pen)

    def _drawGridBackground(self, painter: QPainter):
        """ отрисовка подложки сетки графика """
        if is_logged:
            Journal.log(__name__, "\tdrawing grid background")
        x, y = self._margins[0], self._margins[1]
        painter.fillRect(QRectF(QPointF(0, 0),
                                QSizeF(self.width(),
                                       self.height())),
                         self._style['background'])
        painter.fillRect(QRectF(QPointF(x, y),
                                QSizeF(self.getDrawArea().width(),
                                       self.getDrawArea().height())),
                         self._style['grid']['background'])

    def _drawGridLines_x(self, painter: QPainter, step):
        """ отрисовка линий сетки для оси X """
        if is_logged:
            Journal.log(__name__, "\tdrawing grid lines X")
        axis: Axis = self._charts[self._base_chart].getAxis('x')
        for i, div in axis.generateDivSteps():
            if i == 0 or i == self._divs_x or div == 0.0:
                self._style['grid']['pen'].setStyle(Qt.SolidLine)
            else:
                self._style['grid']['pen'].setStyle(Qt.DotLine)
            coord = i * step + self._margins[0]
            painter.setPen(self._style['grid']['pen'])
            painter.drawLine(QPointF(coord,
                                     self._margins[1]),
                             QPointF(coord,
                                     self.height() - self._margins[3]))

    def _drawGridLines_y(self, painter: QPainter, step: float):
        """ отрисовка линий сетки для оси Y """
        if is_logged:
            Journal.log(__name__, "\tdrawing grid lines Y")
        axis: Axis = self._charts[self._base_chart].getAxis('y')
        for i, div in axis.generateDivSteps():
            if i == 0 or i == self._divs_y or div == 0.0:
                self._style['grid']['pen'].setStyle(Qt.SolidLine)
            else:
                self._style['grid']['pen'].setStyle(Qt.DotLine)
            coord = (self._divs_y - i) * step + self._margins[1]
            painter.setPen(self._style['grid']['pen'])
            painter.drawLine(QPointF(self._margins[0],
                                     coord),
                             QPointF(self.width() - self._margins[2],
                                     coord))

    def _drawGridDivs_x(self, painter: QPainter, step: float):
        """ отрисовка значений делений на оси X """
        if len(self._charts) > 0:
            if is_logged:
                Journal.log(__name__, "\tdrawing grid divisions X")
            axis: Axis = self._charts[self._base_chart].getAxis('x')
            fm = QFontMetricsF(self._style['grid']['font'])
            for i, div in axis.generateDivSteps():
                text = str(round(div, 8))
                offset_x = self._margins[0] - fm.boundingRect(text).width() / 2.0
                offset_y = self.height() - self._margins[3] + fm.height() + 5
                painter.drawText(QPointF(offset_x + i * step,
                                         offset_y),
                                 text)

    def _drawGridDivs_y(self, painter: QPainter, step: float, axis_name='y'):
        """ отрисовка значений делений на оси Y """
        if len(self._charts) > 0:
            if is_logged:
                Journal.log(__name__, f"\tdrawing grid divisions {axis_name}")
            axis: Axis = self._charts[self._base_chart].getAxis(axis_name)
            fm = QFontMetricsF(self._style['grid']['font'])
            for i, div in axis.generateDivSteps():
                text = str(round(div, 8))
                offset_x = self._margins[0] - fm.width(text) - 10
                offset_y = self.height() - self._margins[3] + fm.height() / 4.0
                painter.drawText(QPointF(offset_x,
                                         offset_y - i * step),
                                 text)

    def _drawBorder(self, painter: QPainter):
        """ отрисовка границы области графика """
        if is_logged:
            Journal.log(__name__, "\tdrawing border")
        pen = painter.pen()
        painter.setPen(self._style['grid']['border'])
        painter.drawRect(0, 0,
                         self.getDrawArea().width(),
                         self.getDrawArea().height()
        )
        painter.setPen(pen)

    def _drawCharts(self, painter: QPainter):
        """ отрисовка всех кривых """
        if is_logged:
            Journal.log(__name__, "\tdrawCharts ->")
        transform: QTransform = QTransform()
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)
        self._setTransform(painter, transform)
        for chart in self._charts.values():
            self._drawChart(painter, chart, _flag='a')
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)

    def _drawChart(self, painter: QPainter, chart: Chart, _flag=''):
        """ отрисовка кривой """
        if is_logged:
            Journal.log(__name__, "\tdrawing chart", chart.name)
        if len(chart.getPoints('x')) > 1:
            points = chart.getTranslatedPoints([
                self.getDrawArea().width(),
                self.getDrawArea().height()
            ])
            points = chart.apply_spline(points)
            Graph.drawCurve(painter, points, chart.getPen())
        else:
            Journal.log(__name__, "\tchart", chart.name, "is empty")

    def _updateBaseChart(self, chart: Chart, name: str):
        """ обновление информации об основной кривой """
        if self._base_chart == 'none' or name == 'none':
            if is_logged:
                Journal.log(__name__, "\tupdating base chart to", name)
            self._base_chart = name
            self._divs_x = chart.getAxis('x').getDivs() if chart else 1
            self._divs_y = chart.getAxis('y').getDivs() if chart else 1

    @staticmethod
    def drawLines(painter: QPainter, points):
        """ отрисовка линий по точкам """
        if points.size:
            path: QPainterPath = QPainterPath()
            path.moveTo(points['x'][0], points['y'][0])
            for i in range(1, len(points['x'])):
                path.lineTo(points['x'][i], points['x'][i])
            painter.drawPath(path)

    @staticmethod
    def drawCurve(painter: QPainter, points, pen: QPen):
        """ отрисовка кривой по точкам """
        painter.setPen(pen)
        Graph.drawLines(painter, points)

    @staticmethod
    def drawBezier(painter: QPainter, points: list):
        """ отрисовка кривой Безье по точкам """
        steps = 500
        control_points = [[p.x(), p.y()] for p in points]
        old_point = control_points[0]
        for point in SplineFuncs.bezierCurveRange(steps, control_points):
            painter.drawLine(old_point[0], old_point[1], point[0], point[1])
            old_point = point

    @staticmethod
    def getSpline(points: list):
        """ создание кривой по точкам """
        coords_x, coords_y = Graph.unpackToCoords(points)
        coords_x, coords_y = SplineFuncs.getCurvePoints(coords_x, coords_y)
        result = Graph.packToPoints(coords_x, coords_y)
        return result

    @staticmethod
    def getBSpline(points: list):
        """ создание кубической кривой по точкам """
        coords_x, coords_y = Graph.unpackToCoords(points)
        coords_x, coords_y = SplineFuncs.getBSplinePoints(coords_x, coords_y)
        result = Graph.packToPoints(coords_x, coords_y)
        return result

    @staticmethod
    def unpackToCoords(points: list):
        """ распаковка списка точек в списки координат """
        return points[0], points[1]

    @staticmethod
    def packToPoints(coords_x: list, coords_y: list):
        """ запаковка списков координат в список точек """
        return [coords_x, coords_y]

    def _setTransform(self, painter: QPainter, transform: QTransform):
        transform.scale(1, -1)
        transform.translate(
            self._margins[0],
            -self.getDrawArea().height() - self._margins[1]
        )
        painter.setTransform(transform)

    def _getSteps(self):
        step_x = self.getDrawArea().width() / self._divs_x
        step_y = self.getDrawArea().height() / self._divs_y
        return step_x, step_y
