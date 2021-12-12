"""
    Модуль описывает класс окна информации о типоразмере
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QComboBox, QDialog, QLabel, QLineEdit
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
        # из комбобоксов и чекбоксов
        result = {
            'Producer': self.cmbProducer.currentData()['ID'],
            'Direction': self.cmbDirection.currentIndex(),
            'TestPressure': self.chkPressure.isChecked(),
            'TestThrust': self.chkThrust.isChecked(),
        }
        # остальные из текстовых полей
        result.update({
            item.objectName().replace("txt", ""): \
                item.text() for item in self.findChildren(QLineEdit)
        })
        return result

    def _checkFieldsData(self, data: dict) -> bool:
        """ проверка значений """
        wrong_fields = []
        numeric_fields = ('Rpm', 'Thrust', 'Temp', 'Power')
        for name, value in data.items():
            # проверка числовых значений
            if name in numeric_fields and not value.isnumeric():
                wrong_fields.append(self._getToolTip(QLineEdit, f"txt{name}"))
            # проверка наличия пустых полей
            elif value in (-1, "", None):
                wrong_fields.append(
                    self._getToolTip(
                        QComboBox if value == -1 else QLineEdit,
                        f"cmb{name}" if value == -1 else f"txt{name}"
                    )
                )
        wrong_fields = [field for field in wrong_fields if field != '']
        # вывод сообщение об ошибке
        if wrong_fields:
            wrong_fields.insert(0, "Неверно заполнены поля:")
            Message.show(
                "ОШИБКА",
                '\n  ->'.join(wrong_fields)
            )
            return False
        return True

    def _getToolTip(self, item_type: type, name: str):
        item = self.findChild(item_type, name)
        return item.toolTip() if item else ''

    def _clearFields(self):
        """ очистка полей """
        self.cmbProducer.clear()
        for item in self.findChildren(QLineEdit):
            item.setText("")
