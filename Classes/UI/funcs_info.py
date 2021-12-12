from Classes.Data.alchemy_tables import Customer, Test, Seal
from Classes.UI import funcs_display, funcs_group, funcs_aux
from Classes.UI import funcs_combo, funcs_testlist
from AesmaLib.message import Message


def saveSealInfo(wnd, data_manager, testdata):
    """ сохранение или выбор записи инфрмации о ГЗ """
    # проверяем есть ли такой серийник в базе
    seal_id = data_manager.findRecord(
        Seal,
        lambda x: x.Serial == wnd.cmbSerial.currentText(),
        lambda x: x.Type == data_manager.getTestdata().type_.ID
    )
    # если есть - выбираем
    if seal_id:
        testdata.test_['Seal'] = seal_id
        funcs_display.displaySealInfo(wnd, testdata)
    # проверяем заполение полей и сохраняем
    elif funcs_group.groupCheck(wnd.groupSealInfo):
        seal_info = testdata.seal_
        funcs_group.groupLock(wnd.groupSealInfo, True)
        funcs_group.groupSave(wnd.groupSealInfo, seal_info)
        if data_manager.saveSealInfo():
            funcs_combo.fillCombos_seal(wnd, data_manager)
            wnd.cmbSerial.model().selectContains(seal_info.ID)


def saveTestInfo(wnd, data_manager, testdata):
    """ сохранение или выбор записи информации о тесте """
    testdata.test_['Customer'] = _processCustomer(
        wnd.cmbCustomer.currentText(), data_manager)
    test_id = data_manager.findRecord(
        Test, lambda x: x.OrderNum == wnd.txtOrderNum.text())
    if test_id:
        _selectTest(test_id, wnd)
    elif funcs_group.groupCheck(wnd.groupTestInfo):
        data_manager.clearTestInfo()
        funcs_group.groupSave(wnd.groupTestInfo, testdata.test_)
        funcs_group.groupLock(wnd.groupTestInfo, True)
        data_manager.saveTestInfo()
        # graph_manager.markersClearKnots()
        # graph_manager.drawCharts(wnd.frameGraphInfo)
        funcs_testlist.refresh(wnd, data_manager)


def _processCustomer(value, data_manager):
    """ проверяет есль ли такой заказчик и добавляет если нет """
    id_ = 0
    if value:
        id_ = data_manager.findRecord(Customer, lambda x: x.Name == value)
        if not id_:
            id_ = data_manager.createRecord(Customer, {'Name': value})
    return id_

def _selectTest(test_id, wnd):
    """ запрашивает разрешение и выбирает запись о тесте по ID """
    choice =  Message.choice(
        "Внимание",
        "Запись с таким наряд-заказом "
        "уже присутствует в базе данных.\n"
        "Хотите выбрать её или создать новую?",
        ("Выбрать", "Создать", "Отмена")
    )
    if choice != 2:
        funcs_testlist.setCurrentTest(wnd, test_id)
        if choice == 1:
            funcs_aux.setCurrentDate(wnd)
