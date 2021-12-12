"""
    Модуль содержит функции для работы с комбобоксами главного окна
"""
from AesmaLib.journal import Journal
from Classes.UI import models
from Classes.Data.alchemy_tables import Assembly, Customer, Producer, Type, Seal


@Journal.logged
def fillCombos(window, db_manager):
    """ инициализирует комбобоксы --> """
    fillCombos_test(window, db_manager)
    fillCombos_seal(window, db_manager)


def fillCombos_test(window, db_manager):
    """ инициализирует комбобоксы для теста --> """
    fillCombo_customers(window, db_manager)
    fillCombo_head_base(window, db_manager)


def fillCombos_seal(window, db_manager):
    """ инициализирует комбобоксы для насоса --> """
    fillCombo_producers(window, db_manager)
    fillCombo_types(window, db_manager)
    fillCombo_serials(window, db_manager)


@Journal.logged
def fillCombo_customers(window, db_manager):
    """ --> заполняет заказчик (cmbCustomer) """
    fillCombobox(window.cmbCustomer, db_manager, Customer, ['ID', 'Name'])


@Journal.logged
def fillCombo_head_base(window, db_manager):
    """ --> заполняет сборка (cmbAssembly) """
    fillCombobox(window.cmbHead, db_manager, Assembly, ['ID', 'Name'])
    fillCombobox(window.cmbBase, db_manager, Assembly, ['ID', 'Name'])


@Journal.logged
def fillCombo_producers(window, db_manager):
    """ --> заполняет производитель (cmbProducer) """
    fillCombobox(window.cmbProducer, db_manager, Producer, ['ID', 'Name'])


@Journal.logged
def fillCombo_types(window, db_manager):
    """ --> заполняет типоразмер (cmbType) """
    fillCombobox(window.cmbType, db_manager, Type, ['ID', 'Name', 'Producer'])


@Journal.logged
def fillCombo_serials(window, db_manager):
    """ --> заполняет зав.номер (cmbSerial) """
    fillCombobox(window.cmbSerial, db_manager, Seal, ['ID', 'Serial', 'Type'])


def fillCombo(combo, db_manager, query_params):
    """ инициализирует фильтр и заполняет комбобокс """
    model = models.ComboItemModel(combo)
    display = query_params.columns[1]
    data = None
    data = db_manager.getRecords(query_params)
    data.insert(0, {key: None for key in query_params.columns})
    model.fill(data, display)
    combo.setModel(model)


def fillCombobox(combo, db_manager, table_class, fields):
    """ инициализирует фильтр и заполняет комбобокс """
    model = models.ComboItemModel(combo)
    data = db_manager.getListFor(table_class, fields)
    data.insert(0, {key: None for key in fields})
    model.fill(data, fields[1])
    combo.setModel(model)


def resetFilters_sealInfo(window):
    """ сбрасывает фильт для комбобоксов насоса """
    resetFilter(window.cmbSerial)
    resetFilter(window.cmbType)


def resetFilter(combo):
    """ сбрасывает фильт для комбобокса """
    combo.model().resetFilter()


def selectContains(combo, condition):
    """ выбор элемента, удовлетворяющего условию """
    if not combo.model().checkAlreadySelected(condition):
        combo.model().selectContains(condition)


def filterByCondition(combo, condition):
    """ фильтрация элементов, удовлетворяющих условию """
    if not combo.model().checkAlreadySelected(condition):
        combo.model().applyFilter(condition)
