from reader.configure import config
from reader.LeftTabWidget import LeftTabWidget
from reader.text_filter import TextFilter
from reader.watch_clip import WatchClip
from reader.controller import con
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QMainWindow,
    QGroupBox, QApplication, QLabel, QPlainTextEdit,
    QComboBox
)
import os
import sys
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, pyqtSignal, QEvent, Qt
import platform

sysstr = platform.system()
is_win = is_linux = is_mac = False

if sysstr == "Windows":
    is_win = True
elif sysstr == "Linux":
    is_linux = True
elif sysstr == "Mac":
    is_mac = True

print('System: %s' % sysstr)

MAX_CHARACTERS = 5000


class WebView(QWebEngineView):
    def __init__(self, pdf_path=None):
        print('init webView')
        super(WebView, self).__init__()
        self._glwidget = None
        self.pdf_js_path = "file:///" + \
                           os.path.join(os.getcwd(), "pdfjs",
                                        "web", "viewer.html")
        if pdf_path is None:
            pdf_path = "file:///" + \
                       os.path.join(os.getcwd(), "sample", "sample.pdf")
        if sys.platform == "win32":
            self.pdf_js_path = self.pdf_js_path.replace('\\', '/')
            pdf_path = pdf_path.replace('\\', '/')
        self.changePDF(pdf_path)
        self.setAcceptDrops(True)
        self.installEventFilter(self)

    def dragEnterEvent(self, e):
        """
        Detect mouse drag something into the view

        :param e: Mouse event
        :return: None
        """
        if is_linux or is_mac:
            if e.mimeData().hasFormat('text/plain') and e.mimeData().text()[-6:-2] == ".pdf":
                e.accept()
            else:
                e.ignore()
        elif is_win:
            if e.mimeData().text()[-4:] == ".pdf":
                e.accept()
            else:
                e.ignore()

    def dropEvent(self, e):
        """
        Detect mouse release event the view and state before release is dragging

        :param e: Mouse event
        :return: None
        """
        self.callback_funciton(e.mimeData().text())
        self.changePDF(e.mimeData().text())

    def set_callback_funcition(self, cb_function):
        self.callback_funciton = cb_function

    def event(self, e):
        """
        Detect child add event, as QWebEngineView do not capture mouse event directly,
        the child layer _glwidget is implicitly added to QWebEngineView and we track mouse event through the glwidget

        :param e: QEvent
        :return: super().event(e)
        """
        if self._glwidget is None:
            if e.type() == QEvent.ChildAdded and e.child().isWidgetType():
                print('child add')

                self._glwidget = e.child()
                self._glwidget.installEventFilter(self)
        # if(e.type() == QEvent.ChildRemoved and e.child().isWidgetType()):
        #     # print('child removed')
        #     if(self._glwidget is not None):
        #         self._glwidget.removeEventFilter(self)
        # if(e.type() == QEvent.Close):
        #     # print('close webView')
        #     self.removeEventFilter(self)
        return super().event(e)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonRelease and source is self._glwidget:
            con.pdfViewMouseRelease.emit()
        return super().eventFilter(source, event)

    def changePDF(self, pdf_path):
        self.load(QUrl.fromUserInput('%s?file=%s' %
                                     (self.pdf_js_path, pdf_path)))
        config.set('pdf', 'last', pdf_path)
        config.write(open('CONFIG.ini', 'w'))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.thread_my = WatchClip()
        self.thread_my.start()
        self.setWindowIcon(QIcon('reader.png'))
        self.setWindowTitle("英文PDF阅读器")

        self.translate_ori = QPlainTextEdit()
        self.translate_ori.setStyleSheet("font: 12pt Roboto")
        self.translate_ori.setStyleSheet("background-color:#282828;")  # 文本框内颜色

        self.translate_res = QPlainTextEdit()
        self.translate_res.setStyleSheet("font: 12pt Roboto")
        self.translate_res.setStyleSheet("background-color:#282828;")  # 文本框内颜色

        self.selectable_text_size = [
            '8', '9', '10', '11', '12', '13', '14', '15', ]

        self.text_size_combobox_ori = QComboBox()
        self.text_size_combobox_ori.addItems(self.selectable_text_size)
        self.text_size_combobox_ori.setCurrentIndex(4)
        self.text_size_combobox_ori.setStyleSheet(
            "background-color:qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #494949, stop:1 #3f3f3f);"
            "selection-background-color: #282828;"
            "border:1px solid #282828")

        self.text_size_combobox_res = QComboBox()
        self.text_size_combobox_res.addItems(self.selectable_text_size)
        self.text_size_combobox_res.setCurrentIndex(4)
        self.text_size_combobox_res.setStyleSheet(
            "background-color:qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #494949, stop:1 #3f3f3f);"
            "selection-background-color: #282828;"
            "border:1px solid #282828")

        label1 = QLabel('字体大小:')
        label1.setStyleSheet("background:transparent;")
        label1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label2 = QLabel('字体大小:')
        label2.setStyleSheet("background:transparent;")
        label2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        oriHboxLayout = QHBoxLayout()
        oriHboxLayout.addWidget(QLabel('原文'))
        oriHboxLayout.addWidget(label1)
        oriHboxLayout.addWidget(self.text_size_combobox_ori)
        oriHboxLayout.setStretch(0, 6)
        oriHboxLayout.setStretch(1, 3)
        oriHboxLayout.setStretch(2, 3)
        oriHboxLayout.setContentsMargins(0, 11, 0, 0)
        oriWidget = QWidget()
        oriWidget.setLayout(oriHboxLayout)

        resHboxLayout = QHBoxLayout()
        resHboxLayout.addWidget(QLabel('译文'))
        resHboxLayout.addWidget(label2)
        resHboxLayout.addWidget(self.text_size_combobox_res)
        resHboxLayout.setStretch(0, 6)
        resHboxLayout.setStretch(1, 3)
        resHboxLayout.setStretch(2, 3)
        resHboxLayout.setContentsMargins(0, 0, 0, 0)
        resWidget = QWidget()
        resWidget.setLayout(resHboxLayout)

        self.filter = TextFilter()
        vbox = QVBoxLayout()
        vbox.addWidget(oriWidget)
        vbox.addWidget(self.translate_ori)
        vbox.addWidget(resWidget)
        vbox.addWidget(self.translate_res)
        vbox.setContentsMargins(0, 0, 0, 0)
        # vbox.setMargin(0)

        gbox = QGroupBox('')
        gbox.setStyleSheet("font: 12pt Roboto")
        gbox.setLayout(vbox)
        gbox.setStyleSheet(
            "background-color:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #404040, stop:1 #3f3f3f);")  # 右边框架颜色
        last_pdf = config['pdf']['last']
        if not os.path.exists(last_pdf):
            last_pdf = None
        self.pdfWrapper = WebView(last_pdf)
        self.left_tab_widget = LeftTabWidget(self.pdfWrapper)
        self.pdfWrapper.set_callback_funcition(self.change_leftTab_path)
        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(self.left_tab_widget)
        hBoxLayout.addWidget(self.pdfWrapper)
        hBoxLayout.addWidget(gbox)
        hBoxLayout.setStretch(0, 1)
        hBoxLayout.setStretch(1, 40)
        hBoxLayout.setStretch(2, 12)

        widget = QWidget()
        widget.setLayout(hBoxLayout)
        widget.setStyleSheet(
            "background-color:#282828;color:rgb(250,250,250)")  # 主框架背景颜色
        self.setCentralWidget(widget)
        self.recent_text = ""
        self.showMaximized()

    def change_leftTab_path(self, path):
        self.left_tab_widget.path_now = path[:].replace(
            "%20", " ").replace("\n", "").replace("\r", "").replace("file://", "")

    def updateTranslation(self, cur_text):
        self.translate_res.clear()
        self.translate_res.setPlainText(cur_text)

    def updateByMouseRelease(self):
        if self.pdfWrapper.hasSelection():
            to_translate_text = self.pdfWrapper.selectedText()
            if len(to_translate_text) > MAX_CHARACTERS:
                hint_str = '请选择少于%d个英文字符' % MAX_CHARACTERS
                self.translate_ori.setPlainText(hint_str)
                return
            else:
                if self.recent_text == to_translate_text:
                    return
                else:
                    hint_str = '正在翻译...'
                    filtered = self.filter.removeDashLine(to_translate_text)
                    self.recent_text = to_translate_text
                    self.translate_ori.setPlainText(filtered)
                    self.translate_res.setPlainText(hint_str)

    def updateByTextEdit(self):
        # print('TextEdited')
        self.thread_my.setTranslateText(self.translate_ori.toPlainText())

    def updateOriTextSizeByIndexChanged(self, index):
        self.translate_ori.setStyleSheet(
            "background-color:#282828;"
            "font: {0}pt Roboto".format(self.selectable_text_size[index]))

    def updateResTextSizeByIndexChanged(self, index):
        self.translate_res.setStyleSheet(
            "background-color:#282828;"
            "font: {0}pt Roboto".format(self.selectable_text_size[index]))

    def closeEvent(self, event):
        self.thread_my.expired()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    con.translationChanged.connect(mainWindow.updateTranslation)
    con.pdfViewMouseRelease.connect(mainWindow.updateByMouseRelease)
    mainWindow.translate_ori.textChanged.connect(mainWindow.updateByTextEdit)
    mainWindow.text_size_combobox_ori.currentIndexChanged.connect(
        mainWindow.updateOriTextSizeByIndexChanged)
    mainWindow.text_size_combobox_res.currentIndexChanged.connect(
        mainWindow.updateResTextSizeByIndexChanged)
    sys.exit(app.exec_())
