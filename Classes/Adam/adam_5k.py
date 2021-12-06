"""
    AesmaDiv 2021
    Модуль для работы с Advantech Adam5000TCP
"""
import socket
from time import sleep
from threading import Thread
from dataclasses import dataclass
from enum import Enum
from array import array
from AesmaLib.journal import Journal


class CommandType(Enum):
    """ Типы команды """
    READ = 0    # чтение
    WRITE = 1   # запись
    MULTI = 2   # несколько???


class SlotType(Enum):
    """ Тип слота """
    ALL = 'ALL'
    ANALOG = 'ANALOG'
    DIGITAL = 'DIGITAL'


@dataclass
class Param:
    """ Класс параметров канала """
    slot_type: SlotType
    slot: int
    channel: int
    val_rng: float = 0.0
    offset: int = 0x0
    dig_max: int = 0x0FFF


class CommandBuilder:
    """ Класс строителя комманд """
    def __init__(self, address: int):
        self._address = address
        self._default_commands = {
            SlotType.ANALOG: {
                CommandType.READ: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x4, 0x0, 0x0, 0x0, 0x40
                ]),
                CommandType.WRITE: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x6, 0x0, 0x0, 0x0, 0x0
                ])
            },
            SlotType.DIGITAL: {
                CommandType.READ: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x1, 0x0, 0x0, 0x0, 0x80
                ]),
                CommandType.WRITE: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x5, 0x0, 0x0, 0x0, 0x0
                ])
            }
        }

    def getCommand_default(self, slot_type, command_type):
        """ получение команды по умолчанию """
        return self._default_commands[slot_type][command_type]

    def buildCommand_register(self, command_type, param: Param, value=0):
        """ построение комманды для чтения/записи регистра канала """
        result = self._default_commands[param.slot_type][command_type].copy()
        coef = 8 if param.slot_type == SlotType.ANALOG else 16
        result[9] = coef * param.slot + param.channel
        if command_type == CommandType.READ:
            result[10:] = b'\x00\01'
        elif param.slot_type == SlotType.ANALOG:
            result[10:] = value.to_bytes(length=2, byteorder='big')
        else:
            result[10:] = b'\xff\00' if value else b'\x00\00'
        return result

    def buildCommand_slot(self, slot_type: SlotType, slot: int, pattern: list):
        """ построение комманды для чтения из регистров слота """
        address = slot * (16 if slot_type == SlotType.DIGITAL else 8)
        result = bytearray([self._address, 0xf])
        result.extend(address.to_bytes(2, 'big'))
        if slot_type == SlotType.DIGITAL:
            bits = "".join(['1' if x else '0' for x in pattern])
            bits = bits[::-1]
            values = int(bits, 2).to_bytes(4, 'big')
            result.extend((len(bits) * 2).to_bytes(2, 'big'))
            result.extend((len(values) * 2).to_bytes(1, 'big'))
            for value in values:
                result.extend(value.to_bytes(2, 'little'))
        else:
            result.extend([0x0, 0x8])
            result.extend(pattern)
        prefix = bytearray(len(result).to_bytes(6, 'big'))
        result[0:0] = prefix
        return result


class Adam5K:
    """ Класс для работы с Advantech Adam5000TCP """

    _states = {
        "is_connected": False,
        "is_reading": False,
        "is_paused": False,
        "interval": 1.0
    }

    def __init__(self, host: str, port=502, address=1):
        self._conn = (host, port)
        self._builder = CommandBuilder(address.to_bytes(1, 'big')[0])
        self._sock: socket.socket = None
        self._thread: Thread = None
        self._callback = None
        self._commands = []
        self._data = {
            SlotType.ANALOG: [],
            SlotType.DIGITAL: []
        }

    def __del__(self):
        self.disconnect()
        Journal.log('Adam5K:', '\tdestroyed')

    def setCallback(self, callback):
        """ привязка callback функции """
        self._callback = callback

    def connect(self) -> bool:
        """ подключение """
        if self._states["is_connected"]:
            msg = 'already connected'
        else:
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(0.5)
                self._sock.connect(self._conn)
                self._sock.settimeout(None)
                self._states["is_connected"] = True
                self._states["is_reading"] = False
                msg = 'socket connected'
            except socket.error as ex:
                msg = 'error', self._conn, ex.strerror
        Journal.log(f'Adam5K::connect:\t{msg}')
        return self._states["is_connected"]

    def disconnect(self):
        """ отключение """
        if not self._states["is_connected"]:
            msg = 'not connected'
        else:
            self._states["is_reading"] = False
            while self._thread.is_alive():
                continue
            self._sock.close()
            self._sock = None
            self._states["is_connected"] = False
            msg = 'socket disconnected'
        Journal.log(f'Adam5K::disconnect:\t{msg}')

    def isConnected(self) -> bool:
        """ возвращает статус подключения """
        return self._states["is_connected"]

    def isReading(self) -> bool:
        """ возвращает статус таймера опроса """
        return self._states["is_reading"]

    def isBusy(self):
        """ возвращает занят ли контроллер (есть ли команды в очереди)"""
        return len(self._commands)

    def pause(self):
        """ приостановка опроса """
        self._states["is_paused"] = True

    def unpause(self):
        """ возобновление опроса """
        self._states["is_paused"] = False

    def clearCommands(self):
        """ очистка очереди команд """
        self._commands.clear()

    def setInterval(self, seconds: float):
        """ установка интервала опроса """
        self._states["interval"] = seconds

    def setReadingState(self, state: bool) -> bool:
        """ вкл/выкл режима чтения """
        # проверка подключения
        if not self.isConnected():
            Journal.log('Adam5K::setReadingState:\tnot connected')
            return False
        # проверака текущего статуса потока опроса
        if self.isReading() == state:
            Journal.log(f'Adam5K::setReadingState:\treading state already {state}')
            return False
        # запуск или остановка потока таймера опроса
        _ = self._startThread() if state else self._stopThread()
        Journal.log(f'Adam5K::setReadingState:\tresult {self._states["is_reading"]}')
        return True

    def setChannelValue(self, slot_type: SlotType, slot: int, channel: int, value):
        """ установка значения для канала """
        command = self._builder.buildCommand_register(
            CommandType.WRITE, Param(slot_type, slot, channel), value
        )
        self.sendCommand(command)

    def setSlotValues(self, slot_type: SlotType, slot: int, pattern: list):
        """ установка значений для слота """
        command = self._builder.buildCommand_slot(slot_type, slot, pattern)
        self.sendCommand(command)

    def getValue(self, slot_type: SlotType, slot: int, channel: int):
        """ получение значения канала """
        if not self._states["is_reading"]:
            self.__readAllValues_fromDevice()
        result = self.getValue_fromData(slot_type, slot, channel)
        return result

    def getValue_fromDevice(self, slot_type: SlotType, slot: int, channel: int):
        """ получение значения канала из устройства """
        command = self._builder.buildCommand_register(
            CommandType.READ, Param(slot_type, slot, channel)
        )
        values = self.__execute(command)
        result = values[0]
        if slot_type == SlotType.DIGITAL:
            return result == 1
        return result

    def getValue_fromData(self, slot_type: SlotType, slot: int, channel: int):
        """ чтение значения канала из массива считанных """
        result = 0
        if 0 <= slot < 8 and 0 <= channel < 8:
            if slot_type == SlotType.DIGITAL:
                if len(self._data[slot_type]) == 8:
                    value = self._data[SlotType.DIGITAL][slot]
                    bits = self.__toBits(value)
                    result = bits[channel] == '1'
            else:
                if len(self._data[slot_type]) == 64:
                    result = self._data[slot_type][slot * 8 + channel]
        return result

    def sendCommand(self, command):
        """ отправка команды """
        if self._states["is_connected"]:
            if self._states["is_reading"]:
                self._commands.append(command)
            else:
                _ = self.__execute(command)
        else:
            Journal.log('Adam5K::send command:\t not connected')

    def _startThread(self):
        """ запуск потока опроса """
        self._states["is_reading"] = True
        self._thread = Thread(
            name="Adam5k polling thread",
            target=self._threadPolling
        )
        self._thread.start()

    def _stopThread(self):
        """ остановка потока опроса """
        self._states["is_reading"] = False
        while self._thread.is_alive():
            continue

    def _threadPolling(self):
        """ поток чтения данных из устройства """
        Journal.log('Adam5K::\tзапущен таймер опроса устройства...')
        while self._states["is_reading"]:
            sleep(self._states["interval"])
            if self._states["is_paused"]:
                continue
            thr = Thread(
                name="Adam5k polling subthread",
                target=self._threadTick
            )
            thr.start()
            thr.join()
        Journal.log('Adam5K::\tтаймер опроса устройства остановлен')

    def _threadTick(self):
        """ тик таймера отправки команд в устройство """
        # если в очереди есть комманды - выполнить
        if self._commands:
            command = self._commands.pop(0)
            _ = self.__execute(command)
        # если нет - читать все значения
        else:
            self.__readAllValues_fromDevice()
        # транслировать событие, если есть обработчик
        if self._callback:
            self._callback()

    def __readAllValues_fromDevice(self, slot_type: SlotType = SlotType.ALL):
        """ чтение всех значений в слоте из устройства """
        if slot_type == SlotType.ALL:
            self.__readAllValues_fromDevice(SlotType.ANALOG)
            self.__readAllValues_fromDevice(SlotType.DIGITAL)
        else:
            result = array('H')
            command = self._builder.getCommand_default(slot_type, CommandType.READ)
            data_bytes = self.__execute(command)
            if len(data_bytes) > 8:
                data_count = data_bytes[8]
                data_bytes = data_bytes[9:9 + data_count]
            result = self.__parseBytes(slot_type, data_bytes)
            self._data[slot_type] = result.tolist()

    def __execute(self, command: bytearray):
        """ выполнение команды """
        result = bytearray([])
        self.__read(command, result)
        return result

    def __read(self, command: bytearray, result: bytearray):
        """ запись / чтение из устройства """
        if self.__write(command):
            data = bytearray(self._sock.recv(0x89))
            result.extend(data)

    def __write(self, command: bytes):
        """ запись команды в устройство """
        if self._sock and self._states["is_connected"]:
            return self._sock.send(command) == len(command)
        return False

    @staticmethod
    def __toBits(value: int):
        """ конвертирование значения в биты """
        bits = f"{0:08b}".format(value)
        bits = bits[::-1]
        return bits

    @staticmethod
    def __parseBytes(slot_type: SlotType, slots_data: bytearray):
        """ получение списка байт из массива байт """
        result = array('H')
        if len(slots_data) % 2 > 0:
            slots_data.append(0)
        result.frombytes(slots_data)
        if slot_type == SlotType.ANALOG:
            result.byteswap()
        return result


if __name__ == '__main__':
    adam = Adam5K('10.10.10.11', 502, 1)
    if adam.connect():
        adam.setReadingState(True)
        adam.setSlotValues(SlotType.DIGITAL, 0, [True, False] * 4 * 4)
        adam.setChannelValue(SlotType.ANALOG, 2, 0, 1222)
        val = adam.getValue(SlotType.DIGITAL, 0, 1)
        # adam.set_slot_values(SlotType.DIGITAL, 3, [True] * 8 * 4)
        while adam.isBusy():
            sleep(1.5)
            continue
        adam.setReadingState(False)
        adam.disconnect()
