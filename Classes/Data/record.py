"""
    Модуль описывающий классы для Испытания, Насоса и Типоразмера
"""
import sqlalchemy
from Classes.Data.alchemy_tables import Type, Seal, Test


class Record():
    """ Класс-шаблон описания записи таблицы БД """
    def __init__(self, db_manager, super_class: str, rec_id=0):
        self._db_manager = db_manager
        self._super_class = super_class
        self._props = {}
        _ = self.read(rec_id) if rec_id else self.create()

    def __getitem__(self, key) -> any:
        """ возвращает значение поля записи по имени """
        return self._props[key] if key in self._props else None

    def __setitem__(self, key, value):
        """ задает значение поля записи по имени """
        if key in self._props:
            self._props[key] = value

    def __getattr__(self, name) -> any:
        """ предоставляет доступ к полю записи по имени """
        if name in self._props:
            return self._props[name]
        return None

    def keys(self):
        ''' возвращает список имен столбцов '''
        return self._props.keys()

    def values(self):
        ''' возвращает список значений столбцов '''
        return self._props.values()

    def items(self):
        ''' возвращает список элементы столбцов '''
        return self._props.items()

    def read(self, rec_id) -> bool:
        """ загружает запись из таблицы БД по ID
        -> возвращает успех """
        self.clear()
        def func(**kwargs):
            query = kwargs['session'].query(
                self._super_class
            ).where(self._super_class.ID == rec_id)
            if query.count():
                return query.one().__dict__
            return None
        result = self._db_manager.execute(func)
        if result:
            self._props = {
                k: result[k] for k in self._props.keys()
            }
            return True
        return False

    def create(self) -> bool:
        """ создаёт пустую запись для таблицы БД
        -> возвращает успех """
        self._current = self._super_class()
        table_columns = self._super_class.__table__.columns.keys()
        if table_columns:
            self._props = dict.fromkeys(table_columns)
            return True
        return False

    def clear(self):
        """ очищает все данные в записи """
        self._props = dict.fromkeys(self._props)

    def checkExists(self, conditions: dict=None):
        """ проверяет, существует ли запись с такими условиями """
        if not conditions:
            conditions = [{'ID': self._props['ID']}]
        def func(**kwargs):
            result = kwargs['session'].select(
                self._super_class, ['ID'], conditions
            )
            return result
        items = self._db_manager.execute(func)
        if items:
            return items[0]['ID']
        return 0

    def write(self) -> bool:
        """ сохраняет запись в таблицу БД:
        добавляет новую и сохраняет ID или обновляет существующую
        -> возвращает успех """
        def func(**kwargs):
            data = self._props.copy()
            id_ = data.pop('ID')
            if id_:
                item = kwargs['session'].query(self._super_class).get(id_)
            else:
                item = self._super_class()
            for k in data.keys():
                setattr(item, k, data[k])
            kwargs['session'].add(item)
            try:
                kwargs['session'].commit()
                self._props.update({'ID': item.ID })
            except sqlalchemy.exc.IntegrityError:
                return False
            return item.ID > 0
        return self._db_manager.execute(func)


class RecordType(Record):
    """ Класс информации о типоразмере """
    def __init__(self, db_manager, super_class=Type, rec_id=0):
        super().__init__(db_manager, super_class, rec_id)
        if self.__class__ is RecordType:
            self.ProducerName = ""


class RecordSeal(Record):
    """ Класс информации о насосе """
    def __init__(self, db_manager, super_class=Seal, rec_id=0):
        super().__init__(db_manager, super_class, rec_id)


class RecordTest(RecordType):
    """ Класс информации об испытании """
    def __init__(self, db_manager, super_class=Test, rec_id=0):
        RecordType.__init__(self, db_manager, super_class, rec_id)
        self.values_vbr = []

    def read(self, rec_id) -> bool:
        """ загружает запись из таблицы БД по ID
        -> возвращает успех """
        result = super().read(rec_id)
        if result and self.Vibrations:
            func = lambda x: float(x) if x != '' else 0.0
            values_vbr = list(map(func, self.Vibrations.split(';')))
        return result
