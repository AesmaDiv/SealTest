"""
    Конфигурация Adam5000TCP
    имя_параметра = (слот, канал)
"""
from Classes.Adam.adam_5k import SlotType, Param

IP              = '10.10.10.11'
PORT            = 502
ADDRESS         = 1

params = {
    # "имя": ((тип_слота, слот, канал), (диапазон, смещение, макс.цифр)
    # данные
    "flw0":         Param(SlotType.ANALOG, 2, 0,    1000, 0x0, 0x0FFF),
    "flw1":         Param(SlotType.ANALOG, 2, 0,    1000, 0x0, 0x0FFF),
    "flw2":         Param(SlotType.ANALOG, 2, 0,      80, 0x0, 0x0FFF),
    "rpm":          Param(SlotType.ANALOG, 2, 1,    3000, 0x0, 0x0FFF),
    "torque":       Param(SlotType.ANALOG, 2, 2,     0.2, 0x0, 0x0FFF),
    "psi_in":       Param(SlotType.ANALOG, 2, 3,       0, 0x0, 0x0FFF),
    "psi_out":      Param(SlotType.ANALOG, 2, 3,     3.5, 0x0, 0x0FFF),
    # управление (_ в конце имени)
    "engine_":      Param(SlotType.DIGITAL, 0, 0,      0, 0x0, 0xFF00),
    "flw0_":        Param(SlotType.DIGITAL, 0, 1,      0, 0x0, 0xFF00),
    "flw1_":        Param(SlotType.DIGITAL, 0, 2,      0, 0x0, 0xFF00),
    "flw2_":        Param(SlotType.DIGITAL, 0, 3,      0, 0x0, 0xFF00),
    "valve_":        Param(SlotType.ANALOG,  2, 0,      0, 0x0, 0x0FFF),
    "speed_":        Param(SlotType.ANALOG,  2, 1,      0, 0x0, 0x0FFF),
    # ВРЕМЕННО
    "torque_":      Param(SlotType.ANALOG,  2, 2,      0, 0x0, 0x0FFF),
    "pressure_":    Param(SlotType.ANALOG,  2, 3,      0, 0x0, 0x0FFF),
}
