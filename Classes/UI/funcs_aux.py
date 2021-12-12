"""
    Модуль вспомогательных функций
"""
from datetime import datetime
from AesmaLib.message import Message
from Classes.UI import funcs_group, funcs_combo, funcs_display


def parseFloat(text: str):
    """ безопасная конвертация строки в число с пл.запятой """
    try:
        result = float(text)
    except (ValueError, TypeError):
        result = 0.0
    return result


def calculateLift(sensors: dict):
    """ рассчёт потребляемой мощности """
    psi_in = sensors.get('psi_in', 0)
    psi_out = sensors.get('psi_out', 0)
    lift = (psi_out - psi_in) / 0.433
    return lift


def calculatePower(sensors: dict):
    """ рассчёт потребляемой мощности """
    torque = sensors.get('torque', 0)
    rpm = sensors.get('rpm', 0)
    power = rpm * torque / 5252.0
    return power


def calculateEffs(flws: list, lfts: list, pwrs: list):
    """ расчёт точек КПД """
    result = []
    count = len(flws)
    if count == len(lfts) and count == len(pwrs):
        result = [calculateEff(flws[i], lfts[i], pwrs[i]) \
                for i in range(count)]
    return result


def calculateEff(flw: float, lft: float, pwr: float):
    """ расчёт КПД """
    return 9.81 * lft * flw / (24 * 3600 * pwr) * 100 \
        if flw and lft and pwr else 0


def applySpeedFactor(flw: float, lft: float, pwr: float, rpm: float):
    """ применение фактора скорости """
    if rpm:
        coeff = 2910 / rpm
        flw *= coeff
        lft *= coeff ** 2
        pwr *= coeff ** 3
    return flw, lft, pwr


def setCurrentDate(window):
    """ устанавливает текущую дату-время в соотв.поле """
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    window.txtDateTime.setText(today)


def processMouseWheel(obj, event, coef):
    """ обработка события колесика мыши на полях расход-напор-мощность """
    string = obj.text()
    val = float(string) if string else 0
    val += event.angleDelta().y() / 120 * coef
    val = round(val, 5)
    obj.setText(str(val if val >= 0 else 0))


def askPassword():
    """ проверка пароля """
    result = Message.password(
        'Внимание',
        'Необходимо подтверждение паролем:'
    ) == b'h\x87\x87\xd8\xff\x14LP,\x7f\\\xff\xaa\xfe,\xc5' \
         b'\x88\xd8`y\xf9\xde\x880L&\xb0\xcb\x99\xce\x91\xc6'
    if not result:
        Message.show("ОШИБКА", "Не верный пароль")
    return result
