"""
    Модуль содержит функции для процесса испытания
"""
from PyQt5.QtWidgets import QSlider
from Classes.UI import funcs_table, funcs_aux
from Classes.UI.funcs_aux import parseFloat
from Classes.Adam.adam_manager import AdamManager
from Classes.Adam.adam_config import params


states = {
    "is_running": False,
    "active_flowmeter": "flw2_",
    "points_limit": 10
}
sliders = {
    "sliderFlow": params["valve_"],
    "sliderSpeed": params["speed_"],
    # ВРЕМЕННО
    "sliderTorque": params["torque_"],
    "sliderPressure": params["pressure_"]
}


def prepareSlidersRange(wnd):
    """ установка диапазона слайдеров """
    wnd.radioFlow2.setChecked(True)
    for key, param in sliders.items():
        item = wnd.findChild(QSlider, key)
        if item:
            item.setMaximum(param.dig_max)


def switchControlsAccessible(wnd, state: bool):
    """ переключение доступности кнопок добавления / удаления точек """
    wnd.btnAddPoint.setEnabled(state)
    wnd.btnRemovePoint.setEnabled(state)
    wnd.btnClearCurve.setEnabled(state)
    wnd.btnSaveCharts.setEnabled(not state)
    wnd.spinPointLines.setEnabled(not state)
    wnd.spinPointLines.setMaximum(
        int(wnd.spinPointLines.value()) if state else states["points_limit"]
    )
    wnd.spinPointLines.setValue(wnd.spinPointLines.maximum())


def switchRunningState(wnd, state: bool):
    """ переключение состояния испытания (запущен/остановлен) """
    # if is_logged: Journal.log(__name__, "::\tпереключение состояния теста в",
    #     str(state))
    states["is_running"] = state
    msg = {False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}
    wnd.btnEngine.setText(msg[state])
    wnd.btnSaveCharts.setEnabled(not state)
    wnd.btnGoBack.setEnabled(not state)
    wnd.adam_manager.setValue(params["engine_"], state)


def switchActiveFlowmeter(adam_manager, radio, state):
    """ переключение текущего расходомера """
    flowmeter = {
        "radioFlow0": "flw0_",
        "radioFlow1": "flw1_",
        "radioFlow2": "flw2_"
    }[radio.objectName()]
    states["active_flowmeter"] = flowmeter if state else ""
    adam_manager.setValue(params[flowmeter], state)


def setAdamValue(slider: QSlider, adam_manager: AdamManager, value=-1):
    """ установка значения для канала в соответствии со значением слайдера """
    param = sliders.get(slider.objectName())
    adam_manager.setValue(param, slider.value() if value < 0 else value)


def getCurrentVals(wnd):
    """ получение текущий значений (расход, напор, мощность) из соотв.полей """
    flw = parseFloat(wnd.txtFlow.text())
    lft = parseFloat(wnd.txtLift.text())
    pwr = parseFloat(wnd.txtPower.text())
    eff = calculateEff(flw, lft, pwr)
    return [flw, lft, pwr, eff]


def getCalculatedVals(sensors: dict):
    """ получение расчётных значений  """
    flw = sensors[states["active_flowmeter"].rstrip("_")]
    lft = funcs_aux.calculateLift(sensors)
    pwr = funcs_aux.calculatePower(sensors)
    rpm = sensors.get('rpm', 0)
    flw, lft, pwr = funcs_aux.applySpeedFactor(flw, lft, pwr, rpm)
    return flw, lft, pwr


def switchPointsStagesReal(wnd, test_info):
    """ переключение таблицы точек на ступень / реальные """
    data = funcs_table.getData(wnd.tablePoints)
    if data:
        if wnd.radioPointsReal.isChecked():
            func = lambda x: (x * test_info.seal_['Stages'])
        else:
            func = lambda x: (x / test_info.seal_['Stages'])
        for item in data:
            item['lft'] = round(func(item['lft']), 2)
            item['pwr'] = round(func(item['pwr']), 2)
        funcs_table.setData(wnd.tablePoints, data)


def setControlsDefaults(wnd):
    """ установка слайдеров в исходное положение """
    for name in sliders:
        slider = getattr(wnd, name)
        slider.setValue(0)
        slider.setEnabled(True)


def setAdamDefaults(adam_manager):
    """ установка оборудования в исходное состояние """
    adam_manager.setValue(params["flw0_"],   False)
    adam_manager.setValue(params["flw1_"],   False)
    adam_manager.setValue(params["flw2_"],   True)
    adam_manager.setValue(params["engine_"], False)
    adam_manager.setValue(params["valve_"],  0x0)
    adam_manager.setValue(params["flw0"],    0x0)
    adam_manager.setValue(params["flw1"],    0x0)
    adam_manager.setValue(params["flw2"],    0x0)
    adam_manager.setValue(params["rpm"],     0x0)
    adam_manager.setValue(params["torque"],  0x0)
    adam_manager.setValue(params["psi_in"],  0x0)
    adam_manager.setValue(params["psi_out"], 0x0)
