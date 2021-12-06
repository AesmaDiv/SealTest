"""
    Модуль содержит классы моделей для таблиц и комбобоксов,
    которые описывают механизм отображения элементов
"""
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtCore import QSortFilterProxyModel, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.Qt import QModelIndex


class TemplateTableModel(QAbstractTableModel):
    """ Шаблон модели таблицы """

    def __init__(self, data: list = None, display: list = None, parent=None):
        QAbstractTableModel.__init__(self, parent=parent)
        self._data = [] if data is None else data
        self._display = [] if display is None else display
        self._row_count = len(self._data)
        self._col_count = len(self._display)

    def loadData(self, data: list):
        """ загружает данные из списка """
        self._data.clear()
        self._data = data
        self._row_count = len(data)

    def rowCount(self, _parent=QModelIndex()):
        """ возвращает кол-во строк """
        return self._row_count

    def columnCount(self, _parent=QModelIndex()):
        """ возвращает кол-во столбцов """
        return self._col_count


class ListModel(TemplateTableModel):
    """ Модель таблицы для списка тестов """

    def __init__(self, data: list = None, display: list = None, headers: list = None, parent=None):
        super().__init__(data, display)
        self._headers = [] if headers is None else headers

    def getDisplay(self):
        """ имплементация метода суперкласса (элементы отображения) """
        return self._display

    def setDisplay(self, display: list):
        """ задаёт список элементов (столбцов) для отображения """
        self._display = display

    def getHeaders(self):
        """ имплементация метода суперкласса (заголовоки) """
        return self._headers

    def getData(self):
        """ имплементация метода суперкласса (данные) """
        return self._data

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """ возвращает отображаемое значение """
        if index.isValid():
            row, col = index.row(), index.column()
            data = self._data[row]
            if role == Qt.UserRole:
                return QVariant(data)
            if role == Qt.DisplayRole:
                key = self._display[col]
                if key in data.keys():
                    value = data[key]
                    return value
        return QVariant()

    def headerData(self, col, orientation, role=Qt.DisplayRole):
        """ возвращает заголовок """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._headers[col])
        return QVariant()

    def getRowContains(self, column: int, value, role=Qt.DisplayRole):
        """ возвращает строку содержащую значение """
        result = None
        matches = self.match(self.index(0, column), role, value, -1,
                             flags=Qt.MatchContains | Qt.MatchRecursive)
        if matches:
            result = matches[0]
        return result

    def findContains(self, value, role=Qt.DisplayRole):
        """ возвращает список строк содержащих значение """
        result = []
        matches = self.match(self.index(0, 0), role, value, -1,
                             flags=Qt.MatchContains | Qt.MatchRecursive)
        found_num: int = len(matches)
        if found_num > 0:
            for index in matches:
                data = index.data(Qt.UserRole)
                # data = index.data(Qt.DisplayRole)
                result.append(data)
        return result


class FilterModel(QSortFilterProxyModel):
    """ Модель для фильтра таблиц """

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.parent = parent
        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(0)
        self.parent = parent
        self._filters: list = []
        self._conditions: dict = {}

    def applyFilter(self, filters=None):
        """ применяет фильтр """
        self._filters = filters if isinstance(filters, list) else []
        self._conditions = filters if isinstance(filters, dict) else {}
        self.setFilterFixedString("")

    def resetFilter(self):
        """ сбрасывает фильтр """
        self.applyFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """ применяет фильтр к ряду """
        if self._conditions:
            return self.__filterUserRole(source_row, source_parent)
        if self._filters:
            return self.__filterDisplayRole(source_row, source_parent)
        return True

    def __filterDisplayRole(self, source_row, source_parent):
        """ фильтрует по отображаемым полям """
        result = True
        if self._filters:
            for i, filt in enumerate(self._filters):
                index = self.sourceModel().index(source_row, i, source_parent)
                if index.isValid():
                    data = str(index.data(Qt.DisplayRole))
                    result &= filt in data if data else True
        return result

    def __filterUserRole(self, source_row, source_parent):
        """ фильтрует по скрытым полям """
        if source_row:  # фильтровать все поля кроме нулевого
            index = self.sourceModel().index(source_row, 0, source_parent)
            data = index.data(Qt.UserRole)
            if data and self._conditions:
                for key, value in self._conditions.items():
                    if key in data.keys():
                        return not value or data[key] == value
            return False
        return True


class ComboItemModel(FilterModel):
    """ Класс модели для комбобоксов с фильтрацией """
    _logged = False

    def __init__(self, parent=None):
        FilterModel.__init__(self, parent)
        self.parent = parent
        self._model = QStandardItemModel(0, 0)
        self._display = ""
        self.setSourceModel(self._model)
        self.setDynamicSortFilter(True)

    def fill(self, rows: list, display):
        """ заполняет комбобокс элементами из списка """
        self._display = display
        for _, value in enumerate(rows):
            self._model.appendRow(self.createRow(value))

    def model(self):
        """ возвращает модель """
        return self._model

    def createRow(self, data: dict):
        """ создаёт элемент-строку для комбобокса """
        result = QStandardItem()
        result.setText(data[self._display] if self._display in data \
                           else 'Error')
        result.setData(data, Qt.UserRole)
        return result

    def findIndex(self, value) -> int:
        """ возвращает индекс элемента содержащего значение """
        items = self._model.findItems('', Qt.MatchContains)
        if items:
            # функция поиска если value - словарь
            if isinstance(value, dict):
                key = next(iter(value))
                val = value[key]
                func = lambda data: key in data and data[key] == val
            # -/- если value - значение
            else:
                func = lambda data: value in data.values()
            return next((index for index, item in enumerate(items) \
                         if func(item.data(Qt.UserRole))), 0)
        return 0

    def getItem(self, index=-1):
        """ возвращает элемент по индексу """
        items = self._model.findItems('', Qt.MatchContains)
        if items:
            if index < 0:
                index = self.parent.currentIndex()
                return items[index]
            if 0 <= index < self.rowCount():
                items = self._model.findItems('', Qt.MatchContains)
                return items[index]
        return None

    def selectContains(self, value):
        """ устанавливает текущим элемент содержащий значение """
        self._log(f"=-> {self.parent.objectName()}", "::\t",
                  f"выбор элемента содержащего {value}")
        index = self.findIndex(value)
        self._log(f"=-> {self.parent.objectName()}", "::\t",
                  f"элемент найден по индексу {index}")
        self.applyFilter()
        self.select(index)

    def select(self, index):
        """ устанавливает текущим элемент по индексу """
        if self.parent:
            self._log(f"=-> {self.parent.objectName()}", "::\t",
                      f"выбор индекса {index}")
            self.parent.setCurrentIndex(index)

    def checkAlreadySelected(self, condition):
        """ проверяет выбран ли элемент списка отвечающий условию """
        if condition and self.parent:
            self._log(f"=-> {self.parent.objectName()}", "::\t",
                        f"должен содержать {condition}")
            item = self.parent.currentData()
            self._log(f"=-> {self.parent.objectName()}", "::\t",
                        f"содержит {item}")
            if item:
                if isinstance(condition, dict):
                    key = next(iter(condition))
                    result = key in item and item[key] == condition[key]
                    self._log(f"=-> {self.parent.objectName()}", "::\t",
                                f"результат сравнения {result}")
                    return result
                return condition in item.values()
        return False

    def applyFilter(self, filters=None):
        # self.select(0)
        self._log(f"=-> {self.parent.objectName()}::\t",
                  "применяем новые фильтры:")
        self._log(f"=-> {self.parent.objectName()}::\t",
                  f"текущий фильтр filters    {self._filters}")
        self._log(f"=-> {self.parent.objectName()}::\t",
                  f"текущий фильтр conditions {self._conditions}")
        super().applyFilter(filters)
        self._log(f"=-> {self.parent.objectName()}::\t",
                  f"новый фильтр filters {self._filters}")
        self._log(f"=-> {self.parent.objectName()}::\t",
                  f"новый фильтр conditions {self._conditions}")

    def _log(self, *message):
        if self._logged:
            print(*message)
