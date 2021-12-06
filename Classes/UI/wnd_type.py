"""
    Модуль описывает класс окна информации о типоразмере
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit
from Classes.UI import funcs_combo
from Classes.Data.alchemy_tables import Producer, Type
from AesmaLib.journal import Journal
from AesmaLib.message import Message


class TypeWindow(QDialog):
    """ Класс окна типоразмера """
    def __init__(self, parent, data_manager, path_to_ui):
        super().__init__(parent=parent)
        self._data_manager = data_manager
        self._is_ready = self._createGUI(path_to_ui)

    def addType(self) -> bool:
        """ вызов диалога создания нового типоразмера """
        if self._is_ready:
            self._prepareFields()
            while self.exec_() == QDialog.Accepted:
                data = self._getFieldsData()
                if self._checkFieldsData(data):
                    return self.saveType(data)
        return False

    def saveType(self, type_data: dict) -> bool:
        """ сохраняет информацию о типоразмере """
        if self._is_ready:
            # если производитель не выбран, но указано его имя
            # добавляем нового и выбираем
            if not type_data['Producer'] and type_data['ProducerName']:
                type_data['Producer'] = self._data_manager.createRecord(
                    Producer,
                    {'Name': type_data.pop('ProducerName')}
                )
            # если производитель выбран
            # добавляем новый типоразмер
            if type_data['Producer']:
                result = self._data_manager.createRecord(Type, type_data)
                Message.show(
                    "УСПЕХ" if result else "ОШИБКА",
                    f"Новый типоразмер '{type_data['Name']}' добавлен" \
                        if result else "Ошибка добавление нового типоразмера"
                )
                return result
        return False

    def _createGUI(self, path_to_ui):
        """ загружает файл графического интерфейса """
        try:
            return uic.loadUi(path_to_ui, self) is not None
        except IOError as error:
            Journal.log(__name__, "::\t", "ошибка:", str(error))
        return False

    def _prepareFields(self):
        """ подготовка списка производителей и типоразмера """
        self._clearFields()
        funcs_combo.fillCombo_producers(self, self._data_manager)
        self.cmbProducer.lineEdit().setObjectName("txtProducerName")
        # выбор производителя как в основном окне
        condition = {'ID': self.parent().cmbProducer.currentData()['ID']}
        funcs_combo.selectContains(self.cmbProducer, condition)
        # перенос имени типоразмера из основного окна
        self.txtName.setText(self.parent().cmbType.currentText())

    def _getFieldsData(self) -> dict:
        """ получение значений из полей """
        # производитель из комбобокса
        result = {'Producer': self.cmbProducer.currentData()['ID']}
        # остальные из текстовых полей
        result.update({
            item.objectName().replace("txt", ""): \
                item.text() for item in self.findChildren(QLineEdit)
        })
        return result

    def _checkFieldsData(self, data: dict) -> bool:
        """ проверка значений """
        if not self._checkAllFilled(data):
            return False
        if not self._checkProducer(data):
            return False
        if not self._checkNumeric(data):
            return False
        if not self._checkPoints(data):
            return False
        return True

    def _checkAllFilled(self, data: dict) -> bool:
        """ проверка на заполнение всех полей """
        # список пустых полей
        empty = [key for key, val in data.items() if not val]
        if empty:
            # список соответствующих полям заголовков
            titles = []
            for name in empty:
                lbl = self.findChild(QLabel, f"lbl{name}")
                if lbl:
                    titles.append(f"\n->  {lbl.text()}")
            # создание списка для отображения
            msg = ("").join(titles)
            msg = f"Необходимо заполнить следующие поля:\n{msg}"
            Message.show("Внимание", msg)
            return False
        return True

    @staticmethod
    def _checkProducer(data: dict) -> bool:
        """ проверка производителя """
        if not isinstance(data['Producer'], int):
            Message.show('ОШИБКА', 'Неверно указан производитель')
            return False
        return True

    def _checkNumeric(self, data: dict) -> bool:
        """ проверка числовых значений """
        for name in ('Rpm', 'Min', 'Nom', 'Max'):
            if not data[name].isnumeric():
                elem = self.findChild(QLabel, f'lbl{name}')
                if elem:
                    name = elem.text()
                Message.show('ОШИБКА', f'Поле {name} должно содержать число')
                return False
        return True

    @staticmethod
    def _checkPoints(data: dict) -> bool:
        """ проверка корректности и длины массивов точек """
        try:
            vals_flw = list(map(float, data['Flows'].split(',')))
            vals_lft = list(map(float, data['Lifts'].split(',')))
            vals_pwr = list(map(float, data['Powers'].split(',')))
            if not len(vals_flw) == len(vals_lft) == len(vals_pwr):
                Message.show('ОШИБКА', 'Кол-во значений в полях точек не совпадает')
                return False
        except (TypeError, ValueError):
            Message.show('ОШИБКА', 'Неверный формат в полях точек')
            return False
        return True

    def _clearFields(self):
        """ очистка полей """
        self.cmbProducer.clear()
        for item in self.findChildren(QLineEdit):
            item.setText("")
