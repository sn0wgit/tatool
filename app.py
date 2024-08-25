import sys
import os
from os.path import isfile, isdir, relpath, basename, join
import json
from PyQt6.QtCore import QSize, QModelIndex
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QTabWidget, QWidget, QPushButton, QVBoxLayout, QGridLayout, QLabel, QPlainTextEdit, QTreeView, QFileDialog, QFormLayout, QComboBox, QLineEdit, QMessageBox

class DataInfoWidget(QWidget):
    """Widget for metadata editing"""
    def __init__(self):
        super().__init__()

        self.currentPath = ""
        self.rootPath = ""
        self.metaFile = None
        self.LANGS = ["en", "ru"]
        self.EXPLORER_TYPES = ['explorer.folder', 'explorer.item', 'explorer.variation', 'explorer.jpg', 'explorer.png', 'explorer.svg', 'explorer.webp', 'explorer.a3d', 'explorer.3ds']
        self.currentLanguage = ""
        self.metaFileData:dict = {}
        self.metaFileDataEdited:dict = {}

        self.form = QFormLayout()
        self.setLayout(self.form)

        self.saveButton = QPushButton("Save")
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.forceSave)

        self.previewLabel = QLabel("Preview:")
        self.previewButton = QPushButton("Select file...")
        self.previewButton.clicked.connect(self.updatePreviewImage)
        self.form.addRow(self.previewLabel, self.previewButton)

        self.typeLabel = QLabel("Type:")
        self.typeSelection = QComboBox()
        self.typeSelection.currentIndexChanged.connect(self.typeChangeHandler)
        self.form.addRow(self.typeLabel, self.typeSelection)
        for type in self.EXPLORER_TYPES:
            self.typeSelection.addItem(type)
        self.typeSelection.addItem("")
        self.typeSelection.setCurrentText("")

        self.i18nnameLabel = QLabel("i18nName:")
        self.i18nnameInput = QLineEdit()
        self.i18nnameInput.textChanged.connect(self.i18nNameChangeHandler)
        self.form.addRow(self.i18nnameLabel, self.i18nnameInput)

        self.currentLanguageSelection = QComboBox()
        self.currentLanguageSelection.currentIndexChanged.connect(self.currentLanguageChangeHandler)
        self.form.addWidget(self.currentLanguageSelection)

        self.nameLabel = QLabel("Name:")
        self.nameInput = QLineEdit()
        self.nameInput.textChanged.connect(self.nameChangeHandler)
        self.form.addRow(self.nameLabel, self.nameInput)

        self.descLabel = QLabel("Description:")
        self.descInput = QLineEdit()
        self.descInput.textChanged.connect(self.descriptionChangeHandler)
        self.form.addRow(self.descLabel, self.descInput)
        self.form.addWidget(self.saveButton)

        self.setDisabled(True)

    def updatePreviewImage(self) -> None:
        """Updates preview file. If rejected, then no preview image (`None`)"""
        sourceSelectionHandler = QFileDialog.getOpenFileName(
                parent=self,
                directory=self.currentPath,
                filter="Images (*.jpeg *.jpg *.png *.svg *.webp)"
            )[0] or None
        
        if sourceSelectionHandler != None:
            preview = relpath(
                sourceSelectionHandler,
                start=self.currentPath
            )

            if isdir(self.currentPath):
                preview = "./"+preview

        else:
            preview = None

        self.metaFileDataEdited.update({"preview": preview})

        self.enableSaveButton()

    def typeChangeHandler(self) -> None:
        """Updates new selected data type and removes empty data type, if previously data type was unselected (empty)"""
        if self.typeSelection.currentText() != "":
            self.typeSelection.removeItem(len(self.EXPLORER_TYPES))
            self.enableSaveButton()

            if self.typeSelection.count() == self.EXPLORER_TYPES:
                self.metaFileDataEdited.update({"type": self.typeSelection.currentText()})

    def i18nNameChangeHandler(self) -> None:
        """Updates new inputed data i18n name"""
        self.metaFileDataEdited.update({"namei18n": self.i18nnameInput.text()})
        self.enableSaveButton()

    def currentLanguageChangeHandler(self) -> None:
        """Updates data, if user changes current viewing language"""
        self.currentLanguage = self.currentLanguageSelection.currentText()
        self.setLanguageDependedDatas()

    def setLanguageDependedDatas(self) -> None:
        """Updates data, which depends of language"""
        self.setDataName()
        self.setDataDesc()

    def setDataName(self) -> None:
        """Updates data name (depends of language)"""
        self.nameInput.setText(self.metaFileDataEdited.get(self.currentLanguage+"Name", ""))

    def nameChangeHandler(self) -> None:
        """Updates new inputed data name on selected language"""
        self.metaFileDataEdited.update({self.currentLanguage+"Name": self.nameInput.text()})
        self.enableSaveButton()

    def setDataDesc(self) -> None:
        """Updates data description (depends of language)"""
        self.descInput.setText(self.metaFileDataEdited.get(self.currentLanguage+"Desc", ""))

    def descriptionChangeHandler(self) -> None:
        """Updates new inputed data description on selected language"""
        self.metaFileDataEdited.update({self.currentLanguage+"Desc": self.descInput.text()})
        self.enableSaveButton()

    def predictDataType(self) -> None:
        if isdir(self.currentPath):
            self.typeSelection.setCurrentText(self.metaFileData.get("type", "explorer.folder"))

        elif isfile(self.currentPath):
            if self.currentPath.endswith(".png"):
                self.typeSelection.setCurrentText(self.metaFileData.get("type", "explorer.png"))

            elif self.currentPath.endswith((".jpeg", ".jpg")):
                self.typeSelection.setCurrentText(self.metaFileData.get("type", "explorer.jpg"))
                
            elif self.currentPath.endswith(".svg"):
                self.typeSelection.setCurrentText(self.metaFileData.get("type", "explorer.svg"))
                
            elif self.currentPath.endswith(".webp"):
                self.typeSelection.setCurrentText(self.metaFileData.get("type", "explorer.webp"))
                
            elif self.currentPath.endswith(".a3d"):
                self.typeSelection.setCurrentText(self.metaFileData.get("type", "explorer.a3d"))
                
            elif self.currentPath.endswith(".3ds"):
                self.typeSelection.setCurrentText(self.metaFileData.get("type", "explorer.3ds"))

            else:
                if self.typeSelection.count() == len(self.EXPLORER_TYPES):
                    self.typeSelection.addItem("")
                    self.typeSelection.setCurrentText("")

    def updateMetaFileData(self, data:dict) -> None:
        self.metaFileData = dict(data) # avoids of variable implification instead of value implification

    def setMetaFile(self) -> None:
        """Updates metadata (depends of selected data)"""
        if self.currentLanguageSelection.count() == 0:

            for lang in self.LANGS:
                self.currentLanguageSelection.addItem(lang)

            self.currentLanguage = self.LANGS[0]
            
        if os.access(self.currentPath+".meta", os.R_OK):
            """File opening and overwriting current metadata, based on data from metafile"""
            self.metaFile = open(self.currentPath+".meta", "r")
            metaFileText = self.metaFile.read()
            self.metaFile.close()

            try:
                self.metaFileData = json.loads(metaFileText)
                self.metaFileDataEdited = json.loads(metaFileText)

            except:
                print("Unavaiable to get metadata!\nReason: Metafile is invalid JSON")
                QMessageBox.warning(self, "Unavaiable to get metadata!", "Unavaiable to get metadata!\nReason: Metafile is invalid JSON", buttons=QMessageBox.StandardButton.Ok, defaultButton=QMessageBox.StandardButton.Ok)

                self.metaFileData = {}
                self.metaFileDataEdited = {}
                self.predictDataType()

            self.i18nnameInput.setText(self.metaFileData.get("namei18n", basename(self.currentPath)))
            self.typeSelection.setCurrentText(self.metaFileData.get("type"))

            self.typeSelection.removeItem(len(self.EXPLORER_TYPES))

        else: 
            """Cleaning of metadata, because it is unavailable to open metafile or it does not exist"""
            self.metaFile = None
            self.metaFileData = {}
            self.metaFileDataEdited = {}
            self.predictDataType()
            self.i18nnameInput.setText(basename(self.currentPath))

        self.setLanguageDependedDatas()

    def setCurrentPath(self, path:str) -> None:
        """Updates path for currently selected data.

        :param str path: Absolute path to currently selected data.
        """
        self.currentPath = join(self.rootPath, path)
        self.setMetaFile()
        self.setDisabled(False)

    def setRootPath(self, path:str) -> None:
        """Updates archive root path.

        :param str path: Absolute path to archive root.
        """
        self.rootPath = path

    def setDisabled(self, exp:bool) -> None:
        """Updates avaiability of inputs (except of "Save" button).

        :param bool exp: Negation of enablity ─ if `False`, then enabled, if `True`, then disabled.
        """
        self.previewButton.setDisabled(exp)
        self.typeSelection.setDisabled(exp)
        self.i18nnameInput.setDisabled(exp)
        self.currentLanguageSelection.setDisabled(exp)
        self.nameInput.setDisabled(exp)
        self.descInput.setDisabled(exp)

    def enableSaveButton(self) -> None:
        """Enables save button (if it is possible)"""
        if self.typeSelection.currentText() != "" and self.metaFileDataEdited != self.metaFileData:
            self.saveButton.setDisabled(False)
        else:
            self.saveButton.setDisabled(True)

    def forceSave(self) -> None:
        """Updates metadata on user inputed"""
        metafile = open(self.currentPath+".meta", "w")
        json.dump(self.metaFileDataEdited, metafile, indent=2, ensure_ascii=False) # type: ignore
        metafile.close()
        self.updateMetaFileData(self.metaFileDataEdited)
        self.saveButton.setDisabled(True)

    def isNewMetaDataSaved(self) -> bool:
        """Returns negation of original and edited metadata comparison. If `true`, than they are same (new metadata is saved)"""
        return self.metaFileData == self.metaFileDataEdited

class DataTree(QTreeView):
    """Archive tree-like representation"""
    def __init__(self, dataEditor: DataInfoWidget):
        super().__init__()

        self.rootPath = ""
        self.dataEditor = dataEditor
        self.setHeaderHidden(True)

    def setRootPath(self, path) -> None:
        """Updates archive root path.

        :param str path: Absolute path to archive root.
        """
        self.rootPath = path

    def setDataPath(self, path) -> None:
        """Updates path for currently selected data.

        :param str path: Absolute path to currently selected data.
        """
        self.dataEditor.setCurrentPath(path)

    def currentChanged(self, current: QModelIndex, previous: QModelIndex) -> None:

        if not self.dataEditor.isNewMetaDataSaved():
            criticalWarning = QMessageBox.critical(self, "Save your changes!", "You have edited metadata, but not saved them. Do you want to save?", buttons=QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel, defaultButton=QMessageBox.StandardButton.Save)
            if criticalWarning == QMessageBox.StandardButton.Save:
                self.dataEditor.forceSave()

        def getAllPaths(current: QModelIndex) -> str:
            return join(getAllPaths(current.parent()), current.data()) if str(type(current.parent().data())) == "<class 'str'>" else current.data()
            
        if str(type(current.parent().data())) == "<class 'str'>" or str(type(current.data())) == "<class 'str'>":
            self.allPaths = getAllPaths(current)
            self.setDataPath(self.allPaths)

class DataEditorPage(QWidget):
    """Data editor tab"""
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
        """Method for root path updates.

        :param str path: Absolute path to archive root."""
        self.files.setRootPath(path) # Root update for tree
        self.dataEditor.setRootPath(path) # Root update for data editor

class CompilerPage(QWidget):
    """Compiler tab"""
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
    """Application window"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TATool") # Заголовок окна
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

    def onOpenArchiveButtonClick(self) -> None:
        """Archive folder selection handler"""
        self.rootPath = QFileDialog.getExistingDirectory()

        def appendNonMeta(path:str, parent:QStandardItemModel|QStandardItem) -> None:
            """Loop method to get all archive data, except of `.meta` and `.meta.json` files
            
            :param str path: Absolute parent path.
            :param QStandardItemModel|QStandardItem parent: Parent item (or item model, like root of all items).
            """
            dataNames = [data for data in os.listdir(path) if (isdir(join(path, data)) or (isfile(join(path, data)) and not data.endswith((".meta", ".meta.json"))))]
            for dataName in dataNames:
                dataObject = QStandardItem(dataName)
                dataObject.setEditable(False)
                if isdir(join(path, dataName)):
                    appendNonMeta(join(path, dataName), dataObject)
                parent.appendRow(dataObject)

        if self.rootPath != "": 
            appendNonMeta(self.rootPath, self.dataEditorPage.model) # Fills tree
            self.dataEditorPage.setRootPath(self.rootPath) # Updates root path

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
	
if __name__ == '__main__':
   main()