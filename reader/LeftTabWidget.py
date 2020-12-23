import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qtawesome
import os
from reader.configure import config


class LeftTabWidget(QWidget):
    def __init__(self, pdfWrapper):
        super().__init__()
        self.pdfWrapper = pdfWrapper
        self.setWindowTitle('LTB')
        self.main_layout = QHBoxLayout(self)
        self.path_now = ""
        self.left_widget = QWidget()
        self.main_layout.addWidget(self.left_widget)
        self.button_layout = QVBoxLayout(self.left_widget)

        self.open_file_button = QPushButton(
            qtawesome.icon('fa5s.file-pdf', color='DarkGray'), '')
        self.open_file_button.resize(self.open_file_button.sizeHint())
        self.button_layout.addWidget(self.open_file_button)

        self.open_foder_button = QPushButton(
            qtawesome.icon('fa5s.folder-open', color='DarkGray'), '')
        self.open_foder_button.resize(self.open_foder_button.sizeHint())
        self.button_layout.addWidget(self.open_foder_button)

        self.hide_button = QPushButton(
            qtawesome.icon('fa5s.exchange-alt', color='DarkGray'), '')
        self.hide_button.resize(self.hide_button.sizeHint())
        self.button_layout.addWidget(self.hide_button)

        self.add_button = QPushButton(
            qtawesome.icon('fa5s.bookmark', color='DarkGray'), '')
        self.add_button.resize(self.open_file_button.sizeHint())
        self.button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton(
            qtawesome.icon('fa5.bookmark', color='DarkGray'), '')
        self.remove_button.resize(self.open_file_button.sizeHint())
        self.button_layout.addWidget(self.remove_button)

        self.local_pdf = QPushButton(
            qtawesome.icon('fa5s.list-ul', color='DarkGray'), '')
        self.local_pdf.resize(self.open_file_button.sizeHint())
        self.button_layout.addWidget(self.local_pdf)

        self.favorite_pdf = QPushButton(
            qtawesome.icon('fa5s.th-list', color='DarkGray'), '')
        self.favorite_pdf.resize(self.open_file_button.sizeHint())
        self.button_layout.addWidget(self.favorite_pdf)

        self.info_button = QPushButton(
            qtawesome.icon('fa5s.question', color='DarkGray'), '')
        self.info_button.resize(self.open_file_button.sizeHint())
        self.button_layout.addWidget(self.info_button)

        # stacked_widget as the right widget
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        # resize the stacked_widget
        self.stacked_widget.setMinimumWidth(250)
        # self.left_widget.setMaximumWidth(50)

        # Local PDF
        self.local_pdf_path_list, self.local_pdf_name_list = list(
            self.getLocalPDF(config['pdf']['root']))
        self.list_widget_of_local_pdf = QListWidget()
        self.list_widget_of_local_pdf.addItems(self.local_pdf_name_list)
        self.local_pdf_layout = QVBoxLayout(self.list_widget_of_local_pdf)

        # Favorite PDF
        self.favorite_pdf_path_list, self.favorite_pdf_name_list = self.getFavoritePDF()
        self.list_widget_of_favorite_pdf = QListWidget()
        self.list_widget_of_favorite_pdf.addItems(self.favorite_pdf_name_list)
        self.favorite_pdf_layout = QVBoxLayout(
            self.list_widget_of_favorite_pdf)

        self.form3 = QWidget()
        self.formLayout3 = QHBoxLayout(self.form3)
        self.label3 = QLabel()
        self.label3.setText(
            "")
        self.label3.setSizePolicy(QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.label3.setAlignment(Qt.AlignCenter)
        # self.label3.setFont(QFont("Roman times", 50, QFont.Bold))
        self.formLayout3.addWidget(self.label3)

        # add widgets to stacked_widget
        self.stacked_widget.addWidget(self.list_widget_of_local_pdf)
        self.stacked_widget.addWidget(self.list_widget_of_favorite_pdf)
        self.stacked_widget.addWidget(self.form3)

        # clicked event definition
        # for button
        self.open_file_button.clicked.connect(self.openPdf)
        self.open_foder_button.clicked.connect(self.openFoder)
        self.add_button.clicked.connect(self.addButtonClicked)
        self.remove_button.clicked.connect(self.deleteButtonClicked)
        self.local_pdf.clicked.connect(self.localPDFClicked)
        self.favorite_pdf.clicked.connect(self.favoritePDFClicked)
        self.info_button.clicked.connect(self.on_info_button_clicked)
        self.hide_button.clicked.connect(self.hideButtonClicked)
        # for item
        self.list_widget_of_local_pdf.itemDoubleClicked.connect(
            self.localListWidgetDBClicked)
        self.list_widget_of_favorite_pdf.itemDoubleClicked.connect(
            self.favoriteListWidgetDBClicked)

    def change_leftTab_path(self, path):
        self.path_now = path[:].replace(
            "%20", " ").replace("\n", "").replace("\r", "").replace("file://", "")

    def openPdf(self):
        fd = QFileDialog.getOpenFileName(
            self, '选择一个PDF', './', 'All(*.*);;PDF(*.pdf)', 'PDF(*.pdf)')
        if(fd[0] != ""):
            self.change_leftTab_path(fd[0])
            self.pdfWrapper.changePDF(fd[0])

    def openFoder(self):
        fd = QFileDialog.getExistingDirectory(
            self, '选择一个文件夹', './')
        if(fd != ""):
            config.set('pdf', 'root', fd)
            config.write(open('CONFIG.ini', 'w'))
            self.updateLocal()

    def addButtonClicked(self):
        self.addFavorite()
        self.updateFavorite()

    def deleteButtonClicked(self):
        self.delFavorite()
        self.updateFavorite()

    def favoriteListWidgetDBClicked(self, item):
        for path in self.favorite_pdf_path_list:
            if item.text() in path and item.text() == path[-len(item.text())-4:-4]:
                if(os.path.exists(path)):
                    self.pdfWrapper.changePDF(path)
                    self.path_now = path
                    return

    def localListWidgetDBClicked(self, item):
        for path in self.local_pdf_path_list:
            if item.text() in path and item.text() == path[-len(item.text())-4:-4]:
                self.pdfWrapper.changePDF(path)
                self.path_now = path
                return

    def hideButtonClicked(self):
        self.stacked_widget.setHidden(not self.stacked_widget.isHidden())
        self.local_pdf.setEnabled(not self.stacked_widget.isHidden())
        self.favorite_pdf.setEnabled(not self.stacked_widget.isHidden())
        self.info_button.setEnabled(not self.stacked_widget.isHidden())

    def localPDFClicked(self):
        self.stacked_widget.setCurrentIndex(0)

    def favoritePDFClicked(self):
        self.stacked_widget.setCurrentIndex(1)

    def on_info_button_clicked(self):
        self.stacked_widget.setCurrentIndex(2)

    def getLocalPDF(self, roots=''):
        """
        :param roots: should be absolute path
        :return: pdf path and pdf name
        """
        if roots == 'none':
            return [], []

        def _getFullPath():
            for root, dirs, files in os.walk(roots, topdown=True):
                for name in files:
                    if '.' in name:
                        if name.split('.')[-1] == 'pdf':
                            full_path = os.path.join(root, name)
                            yield full_path.replace('\\', '/')

        def _getFullName():
            for root, dirs, files in os.walk(roots, topdown=True):
                for name in files:
                    if '.' in name:
                        if name.split('.')[-1] == 'pdf':
                            yield name.split('.')[0]

        return list(_getFullPath()), list(_getFullName())

    def getFavoritePDF(self):
        path_list = []
        name_list = []
        try:
            path_list = config['pdf']['favorite'].split("|")
        except:
            return path_list, name_list
        for item in path_list:
            if("/" in item):
                name_list.append(item.split("/")[-1][:-4])
            elif("\\" in item):
                name_list.append(item.split("\\")[-1][:-4])
        return path_list, name_list

    def addFavorite(self):
        if self.path_now in self.favorite_pdf_path_list:
            return
        config['pdf']['favorite'] = "|".join(self.favorite_pdf_path_list) + \
            "|"+self.path_now
        config.write(open('CONFIG.ini', 'w'))

    def delFavorite(self):
        if self.path_now not in self.favorite_pdf_path_list:
            return
        self.favorite_pdf_path_list.remove(self.path_now)
        config['pdf']['favorite'] = "|".join(self.favorite_pdf_path_list)
        config.write(open('CONFIG.ini', 'w'))

    def updateFavorite(self):
        self.favorite_pdf_path_list, self.favorite_pdf_name_list = self.getFavoritePDF()
        self.list_widget_of_favorite_pdf.clear()
        self.list_widget_of_favorite_pdf.addItems(self.favorite_pdf_name_list)

    def updateLocal(self):
        self.local_pdf_path_list, self.local_pdf_name_list = list(
            self.getLocalPDF(config['pdf']['root']))
        self.list_widget_of_local_pdf.clear()
        self.list_widget_of_local_pdf.addItems(self.local_pdf_name_list)
