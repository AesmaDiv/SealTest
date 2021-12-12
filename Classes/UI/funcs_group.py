"""
    Модуль содержит функции для работы с группбоксами главного окна
"""
from typing import Mapping
from PyQt5.QtWidgets import QCheckBox, QGroupBox, QWidget
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox
from PyQt5.QtCore import QRegExp
from AesmaLib.journal import Journal
from AesmaLib.message import Message


def groupDisplay(group: QGroupBox, record, log=False):
    """ отображает информацию записи в полях группы """
    Journal.log(f"{__name__}::\t заполняет поля группы {group.objectName()}")
    for name, value in record.items():
        if name in ('ID', 'Type', 'Producer'):
            continue
        item = group.findChildren(QWidget, QRegExp(name))
        if item:
            if isinstance(item[0], QLineEdit):
                item[0].setText(str(value))
            elif isinstance(item[0], QComboBox):
                item[0].model().selectContains(value)
            elif isinstance(item[0], QCheckBox):
                item[0].setChecked(value if value else False)
            if log:
                Journal.log(f"{item[0].objectName()} <== {value}")


def groupSave(group: QGroupBox, record, log=False):
    """ сохраняет информацию записи в полях группы """
    Journal.log(f"{__name__}::\t сохраняет значения",
                f"из полей группы {group.objectName()}")
    record['ID'] = None
    for name in record.keys():
        item = group.findChildren(QWidget, QRegExp(name))
        if item:
            if isinstance(item[0], QLineEdit):
                record[name] = int(item[0].text()) \
                    if name in ('Stages', "DaysRun") \
                    else item[0].text()
            elif isinstance(item[0], QComboBox):
                record[name] = item[0].currentData()['ID'] \
                    if name in ('Type', 'Producer', 'Customer', 'Assembly') \
                    else item[0].currentText()
            if log:
                Journal.log(f"{item[0].objectName()} ==> {record[name]}")


def groupCheck(group: QGroupBox, log=True):
    """ проверяет заполнение всех полей группы """
    Journal.log(f"{__name__}::\t проверяет заполнение",
                f"всех полей группы {group.objectName()}")
    items = group.findChildren(QLineEdit) + group.findChildren(QComboBox)
    empty_fields = [
        item.toolTip() for item in items
        if (item.objectName().startswith('txt') and not item.text()) or \
        (item.objectName().startswith('cmb') and not item.currentText())
    ]
    if empty_fields:
        empty_fields.insert(0, "Необходимо заполнить поля:")
        Message.show(
            "ВНИМАНИЕ",
             "\n->  ".join(empty_fields)
        )
        return False
    return True


def groupClear(group: QGroupBox):
    """ очищает отображаемую информацию записи в полях группы """
    Journal.log(f"{__name__}::\t очищает поля группы {group.objectName()}")
    widgets = group.findChildren(QWidget)
    for item in widgets:
        if isinstance(item, QLineEdit):
            item.clear()
        elif isinstance(item, QComboBox):
            item.model().resetFilter()
            item.model().select(0)
        elif isinstance(item, QCheckBox):
            item.setChecked(False)
    group.repaint()


def groupLock(group: QGroupBox, state: bool):
    """ блокирует поля группы от изменений """
    Journal.log(f"{__name__}::\t"
                f"{'устанавливает' if state else 'снимает'} блокировку полей группы")
    widgets = group.findChildren(QWidget)
    for item in widgets:
        if isinstance(item, QLineEdit):
            item.setReadOnly(state)
        elif isinstance(item, QComboBox):
            item.setEnabled(not state)
        elif isinstance(item, QPushButton):
            if '_New' in item.objectName():
                _ = item.show() if state else item.hide()
            else:
                _ = item.hide() if state else item.show()
        if state:
            item.clearFocus()
    group.repaint()
