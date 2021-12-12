"""
    Модуль содержит функции для отображения данных в главном окне
"""
from PyQt5.QtWidgets import QLineEdit
from AesmaLib.journal import Journal
from Classes.UI import funcs_table, funcs_group, funcs_test


def displaySensors(window, sensors: dict):
    """ отображает показания датчиков """
    # датчики
    pairs = {
        "txtRPM": "rpm", "txtTorque": "torque",
        "txtPsiIn": "psi_in", "txtPsiOut": "psi_out",
        "txtFlow0": "flw0", "txtFlow1": "flw1", "txtFlow2": "flw2"
    }
    for name, key in pairs.items():
        item = window.findChild(QLineEdit, name)
        if item:
            item.setText(str(round(sensors[key], 2)))
    # расчётные значения
    flw, lft, pwr = funcs_test.getCalculatedVals(sensors)
    window.txtFlow.setText(str(round(flw, 2)))
    window.txtLift.setText(str(round(lft, 2)))
    window.txtPower.setText(str(round(pwr, 4)))


@Journal.logged
def displayRecord(window, data_manager):
    """ отображает информацию о тесте """
    testdata = data_manager.getTestdata()
    funcs_group.groupDisplay(window.groupTestInfo, testdata.test_)
    funcs_group.groupLock(window.groupTestInfo, True)
    displaySealInfo(window, testdata)
    # displayTest_points(window, testdata)


def displaySealInfo(window, testdata):
    """ отображает информацию о насосе """
    seal_id = testdata.test_['Seal']
    Journal.log(f"{__name__}::\t загружает информацию о насосе --> {seal_id}")
    if testdata.seal_.read(seal_id):
        type_id = testdata.seal_['Type']
        Journal.log(f"{__name__}::\t загружает информацию о типе --> {type_id}")
        if testdata.type_.read(type_id):
            funcs_group.groupDisplay(window.groupSealInfo, testdata.seal_)
            funcs_group.groupLock(window.groupSealInfo, True)
            window.groupTestFrame.setTitle(testdata.type_.Name)


def displayMarkerValues(window, data: dict):
    """ отображение текущих значений маркера в соотв.полях """
    name = list(data.keys())[0]
    point = list(data.values())[0]
    if name == 'test_lft':
        window.txtFlow.setText('%.4f' % point.x())
        window.txtLift.setText('%.4f' % point.y())
    elif name == 'test_pwr':
        window.txtPower.setText('%.4f' % point.y())


def displayTest_points(wnd, testdata):
    """ отображение точек испытания в таблице """
    funcs_table.clear(wnd.tablePoints)
    test = testdata.test_
    for i in range(testdata.test_.num_points()):
        flw = test.values_flw[i]
        lft = test.values_lft[i]
        pwr = test.values_pwr[i]
        point_data = (flw, lft, pwr, _, testdata.seal_.Stages)
        funcs_table.addToTable_points(wnd.tablePoints, point_data)
    funcs_table.addToTable_vibrations(wnd.tableVibrations, test.values_vbr)


def displayTest_deltas(window, graph_manager):
    """ отображение результата испытания """
    test_result = graph_manager.generateResultText()
    window.lblTestResult.setText(test_result)


def displayTest_vibrations(window):
    """ отображение показаний вибрации """
    funcs_table.clear(window.tableVibrations)
