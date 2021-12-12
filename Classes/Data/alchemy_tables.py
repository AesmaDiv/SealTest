"""
    Модуль классов связываемых с таблицами базы данных
"""
from dataclasses import dataclass
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BLOB, BOOLEAN, DECIMAL, FLOAT, INTEGER, VARCHAR, String


Base = declarative_base()
@dataclass
class Assembly(Base):
    """ Класс заказчика """
    __tablename__ = 'Assemblies'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Customer(Base):
    """ Класс заказчика """
    __tablename__ = 'Customers'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Producer(Base):
    """ Класс производителя """
    __tablename__ = 'Producers'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Type(Base):
    """ Класс типоразмера """
    __tablename__ = 'Types'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)
    Producer = Column('Producer', INTEGER, ForeignKey("Producers.ID"))
    Date = Column('Date', VARCHAR)
    Rpm = Column('Rpm', FLOAT)
    Thrust = Column('Thrust', FLOAT)
    Temp = Column('Temp', FLOAT)
    Power = Column('Power', FLOAT)
    Direction = Column('Direction', INTEGER)
    TestPressure = Column('TestPressure', BOOLEAN)
    TestThrust = Column('TestThrust', BOOLEAN)
    ProducerName = Column('ProducerName', VARCHAR)


@dataclass
class Seal(Base):
    """ Класс насоса """
    __tablename__ = 'Seals'
    ID = Column('ID', INTEGER, primary_key=True)
    Serial = Column('Serial', VARCHAR)
    Type = Column('Type', INTEGER, ForeignKey('Types.ID'))


@dataclass
class Test(Base):
    """ Класс испытания """
    __tablename__ = 'Tests'
    ID = Column('ID', INTEGER, primary_key=True)
    OrderNum = Column('OrderNum', VARCHAR)
    Customer = Column('Customer', INTEGER, ForeignKey("Customers.ID"))
    Seal = Column('Seal', INTEGER, ForeignKey("Seals.ID"))
    DateReceived = Column('DateReceived', String)
    DateTime = Column('DateTime', String)
    Head = Column('Head', INTEGER, ForeignKey('Assemblies.ID'))
    Base = Column('Base', INTEGER, ForeignKey('Assemblies.ID'))
    Coupling = Column('Coupling', BOOLEAN)
    Coating = Column('Coating', BOOLEAN)
    OilShavings = Column('OilShavings', BOOLEAN)
    OilWater = Column('OilWater', BOOLEAN)
    OilKV = Column('OilKV', DECIMAL)
    Rotation = Column('Rotation', VARCHAR)
    ExtTop = Column('ExtTop', VARCHAR)
    ExtBottom = Column('ExtBottom', VARCHAR)
    Vibrations = Column('Vibrations', VARCHAR)
    Comments = Column('Comments', VARCHAR)
    RawData = Column('RawData', BLOB)
