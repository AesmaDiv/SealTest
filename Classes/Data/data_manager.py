"""
    Модуль описывает структуру хранения информации об испытании
    и класс по управлению этой информацией
"""
from dataclasses import dataclass
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.session import sessionmaker
from Classes.Data.alchemy_tables import Customer, Seal, Test
from Classes.Data.record import Record, RecordType, RecordSeal, RecordTest
from AesmaLib.message import Message
from AesmaLib.journal import Journal


@dataclass
class TestData:
    """ Класс для полной информации об записи """
    def __init__(self, db_manager) -> None:
        self.type_ = RecordType(db_manager)
        self.seal_ = RecordSeal(db_manager)
        self.test_ = RecordTest(db_manager)


class DataManager:
    """ Класс менеджера базы данных """
    def __init__(self, path_to_db) -> None:
        self._path_to_db = path_to_db
        self._engine = create_engine(f'sqlite:///{path_to_db}')
        self._meta = MetaData(self._engine)
        self._testdata = TestData(self)

    def execute(self, func, *args, **kwargs):
        """ выполнение запросов к БД и очистка """
        engine = create_engine(f'sqlite:///{self._path_to_db}')
        Session = sessionmaker(engine)
        with Session() as session:
            kwargs.update({'session': session})
            result = func(*args, **kwargs)
            session.close()
        engine.dispose()
        return result

    def getTestdata(self):
        """ возвращает ссылку на информацию об записи """
        return self._testdata

    def createRecord(self, super_class, data: dict):
        """ создать новую запись """
        record = Record(self, super_class)
        for key, val in data.items():
            record[key] = val
        record.write()
        return record.ID

    @Journal.logged
    def clearRecord(self):
        """ очищает информацию о записи """
        self.clearTypeInfo()
        self.clearSealInfo()
        self.clearTestInfo()
        self._testdata.dlts_ = {}

    def loadRecord(self, test_id: int) -> bool:
        """ загружает информацию о тесте """
        Journal.log_func(self.loadRecord, test_id)
        return self._testdata.test_.read(test_id)

    @Journal.logged
    def removeCurrentRecord(self):
        """ удаляет текущую запись из БД"""
        test_id = self._testdata.test_['ID']
        if test_id:
            session = sessionmaker(self._engine)
            with session() as session_:
                query = session_.query(Test).where(Test.ID == test_id)
                if query.count():
                    session_.delete(query.one())
                    session_.commit()
                session_.close()
                self._engine.dispose()

    def clearTypeInfo(self):
        """ очистка информации о типоразмере """
        self._testdata.type_.clear()

    def clearSealInfo(self):
        """ очистка информации о насосе """
        self._testdata.seal_.clear()

    def clearTestInfo(self):
        """ очистка информации о тесте """
        self._testdata.test_.clear()

    def getTestsList(self):
        """ получает список тестов """
        def func(**kwargs):
            session_ = kwargs['session']
            result = session_.query(
                    Test.ID, Test.DateTime, Test.OrderNum, Seal.Serial
                ).filter(Test.Seal == Seal.ID).order_by(Test.ID.desc()).all()
            return result
        result = self.execute(func)
        return list(map(dict, result))

    def getListFor(self, table_class, fields):
        """ получает список элементов из таблицы """
        def func(**kwargs):
            columns = [getattr(table_class, field) for field in fields]
            result = kwargs['session'].query(*columns).all()
            return result
        result = self.execute(func)
        return list(map(dict, result))

    def findRecord(self, db_class, where_func, filter_func=None):
        """ поиск записи по условию с фильтрацией """
        def func(**kwargs):
            query = kwargs['session'].query(db_class).where(where_func(db_class))
            if filter_func:
                query = query.filter(filter_func(db_class))
            return query.one().ID if query.count() else 0
        return self.execute(func)

    @Journal.logged
    def saveTestInfo(self):
        """ сохраняет информацию о тесте """
        self._testdata.test_['Seal'] = self._testdata.seal_['ID']
        self._testdata.test_.write()

    @Journal.logged
    def saveSealInfo(self) -> bool:
        """ сохраняет информацию о насосе """
        return self._testdata.seal_.write()
