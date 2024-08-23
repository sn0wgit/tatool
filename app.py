import sys
import os
import json
from PyQt6.QtCore import QSize, QModelIndex
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QTabWidget, QWidget, QPushButton, QVBoxLayout, QGridLayout, QLabel, QPlainTextEdit, QTreeView, QFileDialog, QFormLayout, QComboBox, QLineEdit

class DataInfoWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.currentPath = ""
        self.rootPath = ""
        self.metaFile = None
        self.LANGS = ["en", "ru"]
        self.EXPLORER_TYPES = ['explorer.variation', 'explorer.item', 'explorer.folder', 'explorer.jpg', 'explorer.png', 'explorer.svg', 'explorer.a3d', 'explorer.3ds']
        self.currentLanguage = ""
        self.metaFileData:dict = {}

        self.form = QFormLayout()
        self.setLayout(self.form)

        self.previewLabel = QLabel("Preview:")
        self.previewButton = QPushButton("Select file...")
        self.form.addRow(self.previewLabel, self.previewButton)

        self.typeLabel = QLabel("Type:")
        self.typeSelection = QComboBox()
        self.typeSelection.currentIndexChanged.connect(self.typeChangeHandler)
        self.form.addRow(self.typeLabel, self.typeSelection)

        self.i18nnameLabel = QLabel("i18nName:")
        self.i18nnameInput = QLineEdit()
        self.form.addRow(self.i18nnameLabel, self.i18nnameInput)

        self.currentLanguageSelection = QComboBox()
        self.currentLanguageSelection.currentIndexChanged.connect(self.currentLanguageChangeHandler)
        self.form.addWidget(self.currentLanguageSelection)

        self.nameLabel = QLabel("Name:")
        self.nameInput = QLineEdit()
        self.form.addRow(self.nameLabel, self.nameInput)

        self.descLabel = QLabel("Description:")
        self.descInput = QLineEdit()
        self.form.addRow(self.descLabel, self.descInput)

        self.saveButton = QPushButton("Save")
        self.saveButton.setDisabled(True)
        self.form.addWidget(self.saveButton)

        self.setDisabled(True)

    def typeChangeHandler(self) -> None:
        if self.typeSelection.currentText() != "":
            self.typeSelection.removeItem(len(self.EXPLORER_TYPES))

    def currentLanguageChangeHandler(self) -> None:
        self.currentLanguage = self.currentLanguageSelection.currentText()
        self.setLanguageDependedDatas()

    def setLanguageDependedDatas(self) -> None:
        self.setDataName()
        self.setDataDesc()

    def setDataName(self) -> None:
        self.nameInput.setText(self.metaFileData.get(self.currentLanguage+"Name", ""))

    def setDataDesc(self) -> None:
        self.descInput.setText(self.metaFileData.get(self.currentLanguage+"Desc", ""))

    def setMetaFile(self) -> None:
        if self.typeSelection.count() == 0:
            for type in self.EXPLORER_TYPES:
                self.typeSelection.addItem(type)
        if self.currentLanguageSelection.count() == 0:
            for lang in self.LANGS:
                self.currentLanguageSelection.addItem(lang)
            self.currentLanguage = self.LANGS[0]
            
        if os.access(self.currentPath+".meta", os.R_OK):
            print("Accessing", self.currentPath+".meta")
            self.metaFile = open(self.currentPath+".meta", "r")
            self.metaFileText = self.metaFile.read()
            self.metaFileData = json.loads(self.metaFileText)
            self.metaFileDataEdited = json.loads(self.metaFileText)
            self.i18nnameInput.setText(self.metaFileData.get("namei18n", ""))
            self.typeSelection.setCurrentText(self.metaFileData.get("type", ""))
            self.typeSelection.removeItem(len(self.EXPLORER_TYPES))
            self.setLanguageDependedDatas()
            self.metaFile.close()

        else: 
            self.metaFile = None
            self.metaFileData = {}
            self.metaFileDataEdited = {}
            self.metaFileLangs = []
            self.i18nnameInput.setText("")
            if self.typeSelection.count() == len(self.EXPLORER_TYPES):
                self.typeSelection.addItem("")
                self.typeSelection.setCurrentText("")
            self.setLanguageDependedDatas()

    def setCurrentPath(self, path) -> None:
        self.currentPath = os.path.join(self.rootPath, path)
        self.setMetaFile()
        self.setDisabled(False)

    def setRootPath(self, path) -> None:
        self.rootPath = path

    def setDisabled(self, exp:bool):
        self.previewButton.setDisabled(exp)
        self.typeSelection.setDisabled(exp)
        self.i18nnameInput.setDisabled(exp)
        self.currentLanguageSelection.setDisabled(exp)
        self.nameInput.setDisabled(exp)
        self.descInput.setDisabled(exp)

class DataTree(QTreeView):
    def __init__(self, dataEditor: DataInfoWidget):
        super().__init__()

        self.rootPath = ""
        self.dataEditor = dataEditor
        self.setHeaderHidden(True)

    def setRootPath(self, path) -> None:
        self.rootPath = path

    def setDataPath(self, path) -> None:
        self.dataEditor.setCurrentPath(path)

    def currentChanged(self, current: QModelIndex, previous: QModelIndex) -> None:
        def getAllPaths(current: QModelIndex) -> str:
            return os.path.join(getAllPaths(current.parent()), current.data()) if str(type(current.parent().data())) == "<class 'str'>" else current.data()
            
        if str(type(current.parent().data())) == "<class 'str'>" or str(type(current.data())) == "<class 'str'>":
            self.allPaths = getAllPaths(current)
            self.setDataPath(self.allPaths)

class DataEditorPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)

        self.preview = QLabel("Preview")
        self.preview.setStyleSheet("border: 1px solid rgba(255,255,255,0.25);")

        self.dataEditor = DataInfoWidget()

        self.files = DataTree(self.dataEditor)
        self.model = QStandardItemModel()
        self.files.setModel(self.model)

        layout.addWidget(self.preview, 0, 1)
        layout.addWidget(self.dataEditor, 1, 1)
        layout.addWidget(self.files, 0, 0, 0, 1)

    def setRootPath(self, path) -> None:
        self.files.setRootPath(path) # Root update for tree
        self.dataEditor.setRootPath(path) # Root update for data editor

class CompilerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.output = ""
        self.compileButton = QPushButton("Compile!")
        self.compileNote = QLabel("Note: it will overwrite all previous data in .meta.json files!")
        self.compileLogs = QPlainTextEdit(self.output)
        self.compileLogs.setStyleSheet("font-family: monospace;")
        self.compileLogs.setReadOnly(True)
        self.compileLogs.setFixedHeight(463)
        
        self.layout_ = QVBoxLayout()
        self.setLayout(self.layout_)

        self.layout_.addWidget(self.compileButton, 0)
        self.layout_.addWidget(self.compileNote, 0)
        self.layout_.addWidget(self.compileLogs, 0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TO#A™ Archive Tool") # Заголовок окна
        self.setFixedSize(QSize(800, 600)) # Размер окна
        self.rootPath = ""

        menu = self.menuBar()
        if menu != None: file_menu = menu.addMenu("&File") # Первый дроплист верхнего бара

        open_archive_button = QAction("&Open archive", self) # Первая кнопка первого дроплиста из верхнего бара
        open_archive_button.setStatusTip("Select archive root folder") # Описание для статусбара
        open_archive_button.triggered.connect(self.onOpenArchiveButtonClick) # Дефинирование обработчика нажатий

        self.setStatusBar(QStatusBar(self)) # Статусбар (внизу)
        if file_menu != None: file_menu.addAction(open_archive_button) # Добавление первой кнопки

        self.dataEditorPage = DataEditorPage()
        self.compilerPage = CompilerPage()

        self.tab_widget = QTabWidget(self)
        self.tab_widget.move(0, 19)
        self.tab_widget.resize(800, 561)
        self.tab_widget.addTab(self.dataEditorPage, "Data Editor")
        self.tab_widget.insertTab(1, self.compilerPage, "Compiler")

    def onOpenArchiveButtonClick(self):
        self.rootPath = QFileDialog.getExistingDirectory()

        def appendNonMeta(path:str, parent:QStandardItemModel|QStandardItem) -> None:
            dataNames = [data for data in os.listdir(path) if (os.path.isdir(os.path.join(path, data)) or (os.path.isfile(os.path.join(path, data)) and not data.endswith((".meta", ".meta.json"))))]
            for dataName in dataNames:
                dataObject = QStandardItem(dataName)
                dataObject.setEditable(False)
                if os.path.isdir(os.path.join(path, dataName)):
                    appendNonMeta(os.path.join(path, dataName), dataObject)
                parent.appendRow(dataObject)

        if self.rootPath != "": 
            print(self.rootPath)
            appendNonMeta(self.rootPath, self.dataEditorPage.model) # Fills tree
            self.dataEditorPage.setRootPath(self.rootPath) # Updates root path

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
	
if __name__ == '__main__':
   main()