"""
    Модуль журналирования
    logged - декоратор журналирования метода
    log - метод записи сообщения в журнал
"""
from datetime import date


class Journal:
    """ Класс журналирования """
    LOGGED = False
    IS_NUMERATED = True     # вкл/выкл нумерации строк
    WRITE_TO_FILE = False   # вкл/выкл записи в файл
    LINE_NUMBER = 0         # текущий номер строки

    @staticmethod
    def logged(func):
        """ Декоратор журналирования """
        if not Journal.LOGGED:
            return func
        def wrapped(*args, **kwargs):
            if isinstance(func, staticmethod):
                Journal.log_stfunc(func)
                result = func.__func__(*args, **kwargs)
            else:
                Journal.log_func(func)
                result = func(*args, **kwargs)
            return result
        return wrapped

    @staticmethod
    def logged_msg(begin_message = '', end_message = ''):
        """ Декоратор журналирования """
        def wrapped(func):
            if not Journal.LOGGED:
                return func
            def wrap(*args, **kwargs):
                if begin_message != '':
                    Journal.log(func.__name__, '\t', begin_message)
                result = func(*args, **kwargs)
                if end_message != '':
                    Journal.log(func.__name__, '\t', end_message)
                return result
            return wrap
        return wrapped

    @staticmethod
    def log(*messages, end='\n'):
        """ Запись сообщения в журнал """
        if Journal.LOGGED:
            message = " ".join([str(item) for item in messages])
            if Journal.IS_NUMERATED:
                Journal.LINE_NUMBER += 1
                message = str(Journal.LINE_NUMBER) + '> ' + message
            cur_date = date.today().strftime('%Y-%m-%d')
            if Journal.WRITE_TO_FILE:
                with open(cur_date, 'a', encoding='utf-8') as file_:
                    file_.write(message + '\n')
                    file_.close()
            print(message, end=end)

    @staticmethod
    def log_func(func, postfix=""):
        """ журналирование выполняемого метода """
        if Journal.LOGGED:
            Journal.log(f"{func.__module__}::",
                        f"\t{func.__doc__.strip()}",
                        f"--> {postfix}" if postfix else "")

    @staticmethod
    def log_stfunc(func, postfix=""):
        """ журналирование выполняемого статического метода """
        if Journal.LOGGED:
            Journal.log(f"{func.__self__.__class__.__name__}::",
                        f"\t{func.__func__.__doc__.strip()}",
                        f"--> {postfix}" if postfix else "")
