"""
    Модуль содержит функции для работы с таблицами главного окна
"""
from dataclasses import dataclass, field
from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QItemSelectionModel
from Classes.UI import models
from AesmaLib.journal import Journal


@dataclass
class TableParams:
    """ Класс параметров таблицы """
    display: list = field(default_factory=list)
    headers: list = field(default_factory=list)
    data: object = None
    headers_sizes: list = field(default_factory=list)
    headers_resizes: list = field(default_factory=list)
    filter_proxy: QSortFilterProxyModel = None


@Journal.logged
def initTable_points(window):
    """ инициализирует таблицу точек """
    for i, val in enumerate([60, 60, 80, 60]):
        window.tablePoints.setColumnWidth(i, val)
    create(
        window.tablePoints,
        TableParams(
            display=['flw', 'lft', 'pwr', 'eff'],
            headers=['расход\nм³/сут', 'напор\nм', 'мощность\nкВт', 'кпд\n%'],
            headers_sizes=[60, 60, 80, 60],
            headers_resizes=[
                QHeaderView.Stretch,
                QHeaderView.Stretch,
                QHeaderView.Fixed,
                QHeaderView.Stretch
            ]
        )
    )


@Journal.logged
def initTable_vibrations(window):
    """ инициализирует таблицу вибрации """
    window.tableVibrations.setColumnWidth(0, 60)
    window.tableVibrations.setColumnWidth(1, 80)
    create(
        window.tableVibrations,
        TableParams(
            display=['num','vbr'],
            headers=['№','мм/с2'],
            headers_sizes=[60, 80],
            headers_resizes=[QHeaderView.Fixed, QHeaderView.Stretch]
        )
    )


def create(table_view: QTableView, params: TableParams):
    " создание таблицы """
    model = models.ListModel(
        data=params.data, display=params.display, headers=params.headers
    )
    if params.filter_proxy is None:
        params.filter_proxy = QSortFilterProxyModel()
    params.filter_proxy.setSourceModel(model)
    table_view.setModel(params.filter_proxy)
    setHeaders(table_view, params.headers_sizes, params.headers_resizes)


def getData(table_view: QTableView):
    """ получение данных из таблицы """
    proxy = table_view.model()
    current_model = proxy.sourceModel()
    data = current_model.getData()
    return data


def setData(table_view: QTableView, data):
    """ запись данных в таблицу """
    proxy = table_view.model()
    current_model = proxy.sourceModel()
    display, headers = current_model.getDisplay(), current_model.getHeaders()
    new_model = models.ListModel(data=data, display=display, headers=headers)
    proxy.setSourceModel(new_model)
    table_view.setModel(proxy)


def addToTable_points(table_view, point_data: list):
    """ добавление точки в таблицу """
    if len(point_data) == 5:
        data = {
            'flw': round(point_data[0], 1),
            'lft': round(point_data[1], 2),
            'pwr': round(point_data[2], 4),
            'eff': round(point_data[3], 1),
            'lft_real': round(point_data[1] * point_data[4], 2),
            'pwr_real': round(point_data[2] * point_data[4], 2)
        }
        addRow(table_view, data)


def setDisplay(table_view: QTableView, display: list):
    """ установка списка имён столбцов для отображения """
    filter_proxy = table_view.model()
    model = filter_proxy.sourceModel()
    model.setDisplay(display)
    table_view.viewport().update()


def addToTable_vibrations(table_view, vibrations):
    """ добавление вибрации в таблицу """
    for i, vbr in enumerate(vibrations):
        data = {
            'num': i + 1,
            'vbr': round(vbr, 2)
        }
        addRow(table_view, data)


def addRow(table_view: QTableView, row):
    """ добавление строки в таблицу """
    data = getData(table_view)
    data.append(row)
    setData(table_view, data)


def removeLastRow(table_view: QTableView):
    """ удаление последней строки из таблицы """
    data = getData(table_view)
    if data:
        data.pop()
    setData(table_view, data)


def clear(table_view: QTableView):
    """ полная очистка таблицы """
    setData(table_view, [])


def getRow(table_view: QTableView):
    """ получение строки из таблицы """
    try:
        m_index = table_view.currentIndex()
        m_index = m_index.sibling(m_index.row(), m_index.column())
        items = m_index.data(Qt.UserRole)
        return items
    except AttributeError as error:
        Journal.log(__name__ + " error: " + str(error))
        return None
    except TypeError as error:
        Journal.log(__name__ + " error: " + str(error))
        return None


def setHeaders(table_view: QTableView, headers_sizes: list, headers_resizes: list):
    """ установка заголовков столбцов таблицы """
    header = table_view.verticalHeader()
    header.setSectionResizeMode(QHeaderView.Fixed)
    header.setDefaultSectionSize(20)
    header = table_view.horizontalHeader()
    headers_count = min(len(headers_sizes), len(headers_sizes))
    for i in range(headers_count):
        table_view.setColumnWidth(i, headers_sizes[i])
        header.setSectionResizeMode(i, headers_resizes[i])


def selectRow(table_view: QTableView, row: int):
    """ выбор строки в таблице по индексу """
    sel_model = table_view.selectionModel()
    index = table_view.model().sourceModel().index(row, 0)
    mode = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
    sel_model.select(index, mode)
    table_view.setFocus()
