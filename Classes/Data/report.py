"""
    Модуль описания класса протокола об испытании
"""
import os
from jinja2 import FileSystemLoader, Environment
from PyQt5.QtGui import QPageSize
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Classes.Graph.graph_manager import GraphManager
from Classes.Data.data_manager import TestData
from AesmaLib.journal import Journal


class Report:
    """ Класс протокола об испытании """
    _NAMES = {
        "template": "template.html",
        "report": "report.pdf",
        "image": "graph_image.jpg"
    }

    def __init__(self, template_folder, graph_manager: GraphManager, test_data: TestData):
        self._webview = None
        self._printer = None
        self._template_folder = template_folder
        self._test_data = test_data
        self._graph_manager = graph_manager
        self._path_to_img = os.path.join(
            self._template_folder,
            self._NAMES["image"]
        )
        self._base_url = QUrl.fromLocalFile(self._template_folder + os.path.sep)

    @Journal.logged
    def generate(self):
        """ Генерирование протокола """
        if not self._webview:
            self.initPrinter()
        self.__createGraphImage()
        report = self.__create()
        self.__print(report)
        self.__deleteGraphImage()

    def initPrinter(self):
        """ инициализация представления и принтера при первом запросе """
        self._webview = QWebEngineView()
        self._printer = QPrinter(QPrinter.ScreenResolution)
        self._printer.setOutputFormat(QPrinter.NativeFormat)
        self._printer.setPageSize(QPageSize(QPageSize.A4))

    def __loadTemplate(self):
        """ загрузка html шаблона """
        loader = FileSystemLoader(self._template_folder)
        jinja_env = Environment(loader=loader, autoescape=True)
        result = jinja_env.get_template(self._NAMES["template"])
        return result

    def __createGraphImage(self):
        """ сохранение графика испытания в jpg"""
        img_size = QSize(794, 450)
        self._graph_manager.switchPalette('report')
        self._graph_manager.renderToImage(img_size, self._path_to_img)
        self._graph_manager.switchPalette('application')

    def __deleteGraphImage(self):
        if os.path.exists(self._path_to_img):
            os.remove(self._path_to_img)

    @staticmethod
    def __onPrinted(result: bool):
        """ callback вызова печати """
        print(f"Report\t\t->{'успех' if result else 'ошибка'}")

    def __create(self):
        """ создание web страницы протокола """
        result = self.__loadTemplate()
        result = self.__fill(result)
        return result

    def __fill(self, template):
        """ заполнение шаблона данными об испытании """
        context = {
            "seal_info": self._test_data.seal_,
            "test_info": self._test_data.test_,
            "type_info": self._test_data.type_,
            "delta_lft": self._test_data.dlts_['lft'],
            "delta_pwr": self._test_data.dlts_['pwr'],
            "delta_eff": self._test_data.dlts_['eff'],
        }
        result = template.render(context)
        return result

    def __print(self, report):
        """ печать протокола испытания """
        self._webview.setZoomFactor(1)
        self._webview.setHtml(report, baseUrl=self._base_url)
        if QPrintDialog(self._printer).exec_():
            print("Report\t\t->отправка протокола на печать")
            self._webview.page().print(self._printer, self.__onPrinted)
        os.remove(self._path_to_img)
