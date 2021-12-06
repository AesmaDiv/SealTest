"""
    Модуль описывает класс маркеров для графика
"""
from operator import itemgetter
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent, QPoint, QPointF, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame
from Classes.Graph.pump_graph import PumpGraph
from AesmaLib.GraphWidget.chart import Chart
from AesmaLib.journal import Journal


class Markers(QFrame):
    """ Класс маркеров графика """
    eventMove = pyqtSignal(dict)

    def __init__(self, names: list, graph: PumpGraph, parent=None):
        super().__init__(parent)
        self._graph: PumpGraph = graph
        self._point_lines: dict = {
            "vis": False,
            "max": 0,
            "num": 10,
            "cur": 10,
            "pen": QtGui.QPen(Qt.yellow, 2)
        }
        self._names: list = names
        self._markers: dict = {}
        self._area: QFrame = QFrame(self)
        self._initMarkers()
        self._initArea()

    def eventFilter(self, obj: QFrame, event_):
        """ фильтр событий """
        if event_.type() == QEvent.Paint:
            if obj == self._area:
                painter = QtGui.QPainter()
                painter.begin(obj)
                self._drawPointLine(painter)
                self._drawMarkers(painter)
                self._drawKnots(painter)
                painter.end()
            return True
        if event_.type() == QEvent.MouseMove:
            if obj == self._area:
                # funcsTemporary.process_move_marker(obj, e)
                pass
        return super().eventFilter(obj, event_)

    def setPointLinesVis(self, value: bool):
        """ установка видимости для линий отбивания точки """
        self._point_lines['vis'] = value

    def setPointLinesMax(self, value: float):
        """ установка максимального значения расхода для текущего типоразмера """
        pos = self.translatePointToPosition(QPointF(value, 0), "lft")
        self._point_lines['max'] = pos.x()

    def setPointLinesNumber(self, value: int):
        """ установка кол-ва линий для отбивания точек """
        self._point_lines['num'] = value
        self.setPointLinesCurrent(value)

    def setPointLinesCurrent(self, value):
        """ установка значения счетчика текущей точки """
        self._point_lines['cur'] = value

    def getMarkerPosition(self, name: str):
        """ получение координат маркера """
        if name in self._markers:
            return self._markers[name]['pos']
        Journal.log(__name__, 'Error = no such marker')
        return QPointF(0, 0)

    def setMarkerPosition(self, name: str, pos: QPointF):
        """ установка координат маркера """
        if name in self._markers:
            self._markers[name].update({'pos': pos})
        else:
            Journal.log(__name__, 'Error = no such marker')

    def setMarkerColor(self, name: str, color):
        """ установка цвета маркера """
        if name in self._markers:
            self._markers[name].update({'color': color})
        else:
            Journal.log(__name__, 'Error = no such marker')

    def repositionFor(self, graph: PumpGraph):
        """ перенос маркера на другой холст """
        left, top, _, _ = graph.getMargins()
        size = graph.getDrawArea()
        self._area.setGeometry(left, top, size.width(), size.height())

    def addKnots(self):
        """ добавление узлов """
        for name in self._names:
            self.addKnot(name)

    def addKnot(self, name: str):
        """ добавление узла """
        if name in self._markers:
            self._markers[name]['knots'].append(self._markers[name]['pos'])
            self._area.repaint()

    def removeKnots(self):
        """ удаление узлов """
        for name in self._names:
            self.removeKnot(name)

    def removeKnot(self, name: str):
        """ удаление узла по имени """
        if name in self._markers and len(self._markers[name]['knots']) > 0:
            self._markers[name]['knots'].pop()
            self._area.repaint()

    def clearAllKnots(self):
        """ очистка узлов """
        for name in self._names:
            self.clearKnots(name)

    def clearKnots(self, name: str):
        """ очистка узлов по имени """
        if name in self._markers:
            self._markers[name].update({'knots': []})

    def moveMarker(self, point, name: str):
        """ перемещение маркера  по имени """
        pos = self.translatePointToPosition(point, name)
        self._markers[name]['pos'] = pos
        # self.eventMove.emit({name: self.translatePositionToPoint(name)})
        self._area.repaint()

    def createBackground(self):
        """ создание подложки """
        pixmap = QPixmap(self._graph.size())
        self._graph.render(pixmap)
        pixmap.save('render.png')
        self.setStyleSheet("QFrame {background-image: url('render.png');}")
        self._graph.setVisible(False)

    def _initArea(self):
        self._area.installEventFilter(self)
        self._area.setGeometry(1, 1, 10, 10)
        self._area.setFrameShape(QFrame.StyledPanel)
        self._area.setFrameShadow(QFrame.Raised)
        self._area.setStyleSheet(
            "QFrame {"
            "border: 1px solid red;"
            "background: transparent;"
            "}"
        )

    def _initMarkers(self):
        """ инициализация маркеров """
        for name in self._names:
            self._createMarker(name)

    def _createMarker(self, name):
        self._markers.update({
            name: {
                'pos': QPointF(5.0, 5.0),
                'color': Qt.yellow,
                'knots': []
            }
        })

    def _drawPointLine(self, painter):
        """ отрисовка линий, для отбивания точек """
        if self._point_lines['vis'] and self._point_lines['num'] > 2:
            step = (self._point_lines['max']) / (self._point_lines['num'] - 1)
            pen = painter.pen()
            painter.setPen(self._point_lines['pen'])
            pos_x = (self._point_lines['cur'] - 1) * step
            painter.drawLine(QPointF(pos_x, 0.0),
                             QPointF(pos_x, self._area.height()))
            painter.setPen(pen)

    def _drawMarkers(self, painter):
        """ отрисовка маркеров """
        for name in self._names:
            painter.setPen(QtGui.QPen(self._markers[name]['color'], 1))
            self._drawMarker(painter, name)

    def _drawMarker(self, painter, name: str):
        """ отрисовка маркера по имени """
        pos = self._markers[name]['pos']
        painter.drawLine(pos.x() - 5, pos.y(),
                         pos.x() + 5, pos.y())
        painter.drawLine(pos.x(), pos.y() - 5,
                         pos.x(), pos.y() + 5)

    def _drawKnots(self, painter):
        """ отрисовка узлов """
        for name in self._names:
            painter.setPen(QtGui.QPen(self._markers[name]['color'], 1))
            painter.setBrush(QtGui.QBrush(self._markers[name]['color']))
            for point in self._markers[name]['knots']:
                painter.drawEllipse(point.x() - 2, point.y() - 2, 4, 4)

    def translatePositionToPoint(self, position: QPointF, name: str):
        """ пересчёт координат из значений в пиксели """
        result: QPoint = QPointF(0.0, 0.0)
        etalon: Chart = self._graph.getChart(name.replace('test_', ''))
        if etalon is not None:
            size = self._area.size()
            max_x = etalon.getAxis('x').getMaximum()
            max_y = etalon.getAxis('y').getMaximum()
            result.setX(max_x * position.x() / size.width())
            result.setY(max_y * (size.height() - position.y()) / size.height())
        return result

    def translatePointToPosition(self, point: QPointF, name: str):
        """ пересчёт координат из пикселей в значения """
        result: QPoint = QPointF(0.0, 0.0)
        etalon: Chart = self._graph.getChart(name.replace('test_', ''))
        if etalon is not None:
            size = self._area.size()
            max_x = etalon.getAxis('x').getMaximum()
            max_y = etalon.getAxis('y').getMaximum()
            result.setX(size.width() * point.x() / max_x)
            result.setY(size.height() * (1 - point.y() / max_y))
        return result

    def _addPointToKnots(self, name: str, point_x, point_y):
        """ добавление точки к узлам """
        if name in self._markers[name]['knots']:
            self._markers[name]['knots'].append((point_x, point_y))
        else:
            self._createMarker(name)
            self._addPointToKnots(name, point_x, point_y)

    def _getSortedPoints(self, name: str):
        """ получение отсортированных точек """
        points = sorted(self._markers[name]['knots'], key=itemgetter(0))
        points_x, points_y = zip(*points)
        return list(points_x), list(points_y)
