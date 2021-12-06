"""
    Модуль содержит классы для работы с Advantech ADAM 5000 TCP
"""
from PyQt5.QtCore import pyqtSignal, QObject
from AesmaLib.journal import Journal
from Classes.Adam.adam_5k import Adam5K, Param, SlotType
from Classes.Adam import adam_config as adam


class AdamManager(QObject):
    """ Класс для связи контроллера Adam5000TCP с интерфейсом программы """
    _signal = pyqtSignal(dict, name="dataReceived")
    _probes = 10
    _sensors = {
        'rpm': [0.0] * _probes,
        'torque': [0.0] * _probes,
        'psi_in': [0.0] * _probes,
        'psi_out': [0.0] * _probes,
        'flw0': [0.0] * _probes,
        'flw1': [0.0] * _probes,
        'flw2': [0.0] * _probes
    }

    def __init__(self, host, port=502, address=1, parent=None) -> None:
        super().__init__(parent=parent)
        self._adam = Adam5K(host, port, address)
        self._adam.setCallback(self.__adamThreadTickCallback)

    def setPollingState(self, state: bool, interval=1):
        """ вкл/выкл опрос устройства """
        if state and self._adam.connect():
            self._adam.setInterval(interval)
            return self._adam.setReadingState(True)
        self._adam.setReadingState(False)
        self._adam.disconnect()
        return False

    def setValue(self, param: Param, value: int) -> bool:
        """ установка значения для канала """
        if self.checkParams(param, value):
            self._adam.setChannelValue(
                param.slot_type, param.slot, param.channel, value
            )
            return True
        return False

    @staticmethod
    def checkParams(params: Param, value) -> bool:
        """ проверка параметров """
        if params.slot_type in (SlotType.ANALOG, SlotType.DIGITAL):
            if 0 <= params.slot < 8 and 0 <= params.channel < 8:
                if 0 <= value <= params.dig_max:
                    return True
        return False

    def __adamThreadTickCallback(self):
        """ тик таймера опроса устройства """
        self.__updateSensors()
        args = self.__createEventArgs()
        try:
            self._signal.emit(args)
        except RuntimeError as err:
            self._adam.disconnect()
            Journal.log(err.args)

    def __updateSensors(self):
        for key in self._sensors:
            if not self._adam.isReading():
                self._sensors[key] = [0.0] * self._probes
                continue
            param = adam.params[key]
            value = self._adam.getValue(
                param.slot_type, param.slot, param.channel
            )
            value = param.val_rng * (value - param.offset) / param.dig_max
            self._sensors[key].pop(0)
            self._sensors[key].append(round(value, 2))

    def __createEventArgs(self):
        return {
            key: sum(vals)/len(vals) for key, vals in self._sensors.items()
        }
