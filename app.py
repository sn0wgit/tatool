import datetime
import sys
import os
from os.path import isfile, isdir, relpath, abspath, basename, join
import json
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QSize, QModelIndex, Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QAction, QPixmap, QResizeEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QTabWidget, QWidget, QPushButton, QVBoxLayout, QGridLayout, QLabel, QPlainTextEdit, QTreeView, QFileDialog, QFormLayout, QComboBox, QLineEdit, QMessageBox, QCheckBox

class PreviewWidget(QWidget):
    """Widget for preview viewing"""
    def __init__(self):
        super().__init__()

        self.layout_ = QVBoxLayout()
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.setLayout(self.layout_)

        self.currentPreviewPath = ""
        self.currentPreview = None
        self.currentPreviewSVG = QSvgWidget(self.currentPreviewPath, self)
        self.currentPreviewSVG.adjustSize()
        self.currentPreviewImage = QLabel()
        self.currentPreviewImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.currentPreviewLabel = QLabel(basename(self.currentPreviewPath))
        self.currentPreviewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.currentPreviewImage.setHidden(True)
        self.layout_.addWidget(self.currentPreviewSVG)
        self.layout_.addWidget(self.currentPreviewImage)
        self.layout_.addWidget(self.currentPreviewLabel)

    def setPreviewPath(self, path:str|None):
        """Updates preview absolute path
        
        :param str path: Absolute path to the preview file"""
        self.currentPreviewPath = path
        if self.currentPreviewPath != None:
            self.currentPreviewLabel.setText(basename(self.currentPreviewPath))
            if self.currentPreviewPath.endswith(".svg"):
                self.currentPreviewImage.setHidden(True)
                self.currentPreviewSVG.setHidden(False)

            else:
                self.currentPreviewSVG.setHidden(True)
                self.currentPreview = QPixmap(self.currentPreviewPath)
                self.currentPreviewImage.setPixmap(self.currentPreview)
                self.currentPreviewImage.setHidden(False)
        
        else:
            if isinstance(self.currentPreviewSVG, QSvgWidget):
                self.currentPreviewSVG.setHidden(True)
            self.currentPreviewImage.setHidden(True)
            self.currentPreviewLabel.setText("No preview provided")

class DataInfoWidget(QWidget):
    """Widget for metadata editing"""
    def __init__(self, previewWidget:PreviewWidget):
        super().__init__()

        self.currentPath = ""
        self.rootPath = ""
        self.metaFile = None
        self.LANGS = ["en", "ru"]
        self.EXPLORER_TYPES = [
            'explorer.folder', 'explorer.item', 'explorer.variation', 'explorer.jpg', 'explorer.png',
            'explorer.svg', 'explorer.webp', 'explorer.a3d', 'explorer.3ds'
        ]
        self.currentLanguage = ""
        self.metaFileData:dict = {}
        self.metaFileDataEdited:dict = {}
        self.previewWidget = previewWidget

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
        absolutePreviewPath = QFileDialog.getOpenFileName(
                parent=self,
                directory=self.currentPath,
                filter="Images (*.jpeg *.jpg *.png *.svg *.webp)"
            )[0] or None
        
        if absolutePreviewPath != None:
            self.previewWidget.setPreviewPath(absolutePreviewPath)
            preview = relpath(
                absolutePreviewPath,
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
                QMessageBox.warning(
                    self,
                    "Unavaiable to get metadata!",
                    "Unavaiable to get metadata!\nReason: Metafile is invalid JSON",
                    buttons=QMessageBox.StandardButton.Ok,
                    defaultButton=QMessageBox.StandardButton.Ok
                )

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

        if isdir(self.currentPath):
            os.chdir(self.currentPath)
        elif isfile(self.currentPath):
            os.chdir(self.currentPath[:-len(basename(self.currentPath))-1])
        else:
            raise Exception("Nothing to refer. Seems like you deleted archive data.")
        
        if self.metaFileData.get("preview", None) != False and self.metaFileData.get("preview", None) != None:
            self.previewWidget.setPreviewPath(
                abspath(
                        self.metaFileData.get("preview", "")
                        if not self.metaFileData.get("preview", "").startswith("./")
                        else self.metaFileData.get("preview", "")[2:]
                )
            )
            
        else:
            self.previewWidget.setPreviewPath(None)

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
        """Returns original and edited metadata comparison. If `true`, than they are same (new metadata is saved)"""
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
            criticalWarning = QMessageBox.critical(
                self,
                "Save your changes!",
                "You have edited metadata, but not saved them. Do you want to save?",
                buttons= QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                defaultButton=QMessageBox.StandardButton.Save
            )
            if criticalWarning == QMessageBox.StandardButton.Save:
                self.dataEditor.forceSave()

        def getAllPaths(current: QModelIndex) -> str:
            return join(getAllPaths(current.parent()), current.data()) if isinstance(current.parent().data(), str) else current.data()
            
        if isinstance(current.parent().data(), str) or isinstance(current.data(), str):
            self.allPaths = getAllPaths(current)
            self.setDataPath(self.allPaths)

class MetametadataEditorPage(QWidget):
    """Metadata editor tab"""
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)

        self.preview = PreviewWidget()

        self.dataEditor = DataInfoWidget(self.preview)

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
        self.dataEditor.setRootPath(path) # Root update for metadata editor

class CompilerPage(QWidget):
    """Compiler tab"""
    def __init__(self, metadataEditorPage: MetametadataEditorPage):
        super().__init__()

        self.output = ""
        self.APP_DIRECTORY = os.getcwd()
        self.metadataEditorPage = metadataEditorPage


        self.compileButton = QPushButton("Compile!")
        self.compileButton.setDisabled(True)
        self.compileButton.clicked.connect(self.compileButtonHandler)


        self.compileNote = QLabel("Note: it will overwrite all previous data in .meta.json files!")


        self.dumpLogsToggle = QCheckBox()

        self.dumpLogsLabel = QLabel("Dump logs to file")

        self.dumpLogForm = QWidget()
        self.dumpLogFormLayout = QFormLayout()
        self.dumpLogFormLayout.addRow(self.dumpLogsToggle, self.dumpLogsLabel)
        self.dumpLogForm.setLayout(self.dumpLogFormLayout)

        self.compileLogs = QPlainTextEdit(self.output)
        self.compileLogs.setPlaceholderText("Logs")
        self.compileLogs.setStyleSheet("font-family: monospace;")
        self.compileLogs.setReadOnly(True)
        

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.compileButton, alignment = Qt.AlignmentFlag.AlignCenter)
        self.layout_.addWidget(self.compileNote, 0)
        self.layout_.addWidget(self.dumpLogForm)
        self.layout_.addWidget(self.compileLogs, 0)
        self.setLayout(self.layout_)

    def log(self, *args) -> None:
        """Simpilfies to log compiler actions.
        
        :param *args: Any arguments can be passed"""
        log = ""
        for argindx, arg in enumerate(args):
            if argindx != 0:
                log += " "
            log += str(arg)

        print(self.output)

        if self.output == "":
            self.output  = str(datetime.datetime.now()).replace(":", "-")[:19]
        self.output += "\n" + log

        self.compileLogs.setPlainText(self.output)

    def setRootPath(self, path:str, setDiabled=False):
        """Method for root path updates.

        :param str path: Absolute path to archive root.
        :param bool setDiabled: Sets if "Compile" button will be disabled."""
        self.rootPath = path
        self.compileButton.setDisabled(setDiabled)

    def compileButtonHandler(self):
        """Starts compilation from archive root folder."""

        if not self.metadataEditorPage.dataEditor.isNewMetaDataSaved():
            criticalWarning = QMessageBox.critical(
                self,
                "Save your changes!",
                "You want to compile archive, but you have unsaved new metadata.\nDo you want to save it and then compile?",
                buttons= QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Abort | QMessageBox.StandardButton.Discard,
                defaultButton=QMessageBox.StandardButton.Save
            )
            if criticalWarning == QMessageBox.StandardButton.Save:
                self.metadataEditorPage.dataEditor.forceSave()
                
                self.compile(self.rootPath)
                if self.dumpLogsToggle.isChecked():
                    currentDate = str(datetime.datetime.now()).replace(":", "-")[:19]
                    dump = open(join(self.APP_DIRECTORY, f"{currentDate}.log"), "w")
                    dump.write(self.output)
                    dump.close()

            elif criticalWarning == QMessageBox.StandardButton.Cancel:
                self.compile(self.rootPath)
                if self.dumpLogsToggle.isChecked():
                    currentDate = str(datetime.datetime.now()).replace(":", "-")[:19]
                    dump = open(join(self.APP_DIRECTORY, f"{currentDate}.log"), "w")
                    dump.write(self.output)
                    dump.close()

    def compile(self, CURRENT_DIRECTORY:str) -> None:
        """Inspects all `.meta` files and creates on them based `*.meta.json` files.
        `*` are "arrangement" and all language codes, which where found inside CURRENT_DIRECTORY `.meta` files.
        
        :param str CURRENT_DIRECTORY: Current directory to inspect. If contains any directory, than used
        recursion and `CURRENT_DIRECTORY` becomes to `CURRENT_DIRECTORY` subdirectories"""
        self.log("Current directory:", CURRENT_DIRECTORY.replace(self.rootPath, "")+"/")

        directoryMetafiles:list[str] = sorted(
            [
                content
                for content
                in os.listdir(CURRENT_DIRECTORY)
                if isfile(join(CURRENT_DIRECTORY, content))
                and content.endswith(".meta")
            ]
        )
        currentArrangement:dict[
            str, list[
                dict[
                    str, str|bool|None
                ]
                |
                str
            ]
        ] = {"content": [], "breadcrumbs": []}
        allTranslations:dict = {}

        for metafile in directoryMetafiles:

            arrangementForCurrentData:dict[str, str|bool|None] = {}

            currentMetafile = open(join(CURRENT_DIRECTORY, metafile), "r")
            currentMetafileJSONized:dict[str, str|bool|None] = json.loads(currentMetafile.read())
            currentMetafile.close()

            typeFromMetafile:str = currentMetafileJSONized.get("type")                    # type: ignore
            previewFromMetafile:str|bool|None = currentMetafileJSONized.get("preview", None)
            URLFromMetafile:str = currentMetafileJSONized.get("url")                      # type: ignore
            namei18nFromMetafile:str = currentMetafileJSONized.get("namei18n")            # type: ignore

            arrangementForCurrentData.update({"type": typeFromMetafile})
            arrangementForCurrentData.update({"preview": previewFromMetafile})
            arrangementForCurrentData.update({"url": URLFromMetafile})
            arrangementForCurrentData.update({"name": namei18nFromMetafile})

            languageCodes = [key[:2] for key in currentMetafileJSONized.keys() if key.endswith("Desc")]
            for languageCode in languageCodes:
                if allTranslations.get(languageCode, {}) == {}:
                    allTranslations.update({languageCode: {namei18nFromMetafile: {}}})
                nameAndDescription = {}
                nameAndDescription.update({"name": currentMetafileJSONized.get(languageCode+"Name", "")})
                nameAndDescription.update({"description": currentMetafileJSONized.get(str(languageCode+"Desc"), "")})
                allTranslations[languageCode][namei18nFromMetafile] = nameAndDescription

            currentArrangement["content"].append(arrangementForCurrentData)

        if currentArrangement != {"content": [], "breadcrumbs": []}:

            if CURRENT_DIRECTORY.replace(self.rootPath, "")[1:] == "":
                currentArrangement["breadcrumbs"] = []
            else: 
                currentArrangement["breadcrumbs"] = [dir for dir in CURRENT_DIRECTORY.replace(self.rootPath, "")[1:].split(sep="/")]

            currentArrangementFile = open(join(CURRENT_DIRECTORY, "arrangement.meta.json"), "w")
            json.dump(currentArrangement, currentArrangementFile, indent=2, ensure_ascii=False)
            currentArrangementFile.close()

            self.log(f'"{CURRENT_DIRECTORY.replace(self.rootPath, "")}/arrangement.meta.json" created!')

            for language in allTranslations.keys():

                current_translation_file = open(join(CURRENT_DIRECTORY, language+".meta.json"), "w")
                json.dump(allTranslations[language], current_translation_file, indent=2, ensure_ascii=False)
                currentArrangementFile.close()

                self.log(f'"{CURRENT_DIRECTORY.replace(self.rootPath, "")}/{language}.meta.json" created!')

        for directory in sorted(
            [
                directory
                for directory
                in os.listdir(CURRENT_DIRECTORY)
                if os.path.isdir(join(CURRENT_DIRECTORY, directory))
            ]
        ):
            self.compile(join(CURRENT_DIRECTORY, directory))

class MainWindow(QMainWindow):
    """Application window"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TATool")
        self.setMinimumSize(QSize(800, 600))
        self.rootPath = ""

        menu = self.menuBar()
        if menu != None: fileMenu = menu.addMenu("&File")

        openArchiveButton = QAction("&Open archive", self)
        openArchiveButton.setStatusTip("Select archive root folder")
        openArchiveButton.triggered.connect(self.onOpenArchiveButtonClick)

        self.setStatusBar(QStatusBar(self)) # Статусбар (внизу)
        if fileMenu != None: fileMenu.addAction(openArchiveButton)

        self.metadataEditorPage = MetametadataEditorPage()
        self.compilerPage = CompilerPage(self.metadataEditorPage)
        self.tabWidget = QTabWidget(self)
        self.tabWidget.move(0, 19)
        self.tabWidget.resize(self.width(), self.height()-39)
        self.tabWidget.addTab(self.metadataEditorPage, "Metadata Editor")
        self.tabWidget.insertTab(1, self.compilerPage, "Compiler")

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self.tabWidget.resize(self.width(), self.height()-39)

    def onOpenArchiveButtonClick(self) -> None:
        """Archive folder selection handler"""
        self.rootPath = QFileDialog.getExistingDirectory()

        def appendNonMeta(path:str, parent:QStandardItemModel|QStandardItem) -> None:
            """Loop method to get all archive data, except of `.meta` and `.meta.json` files
            
            :param str path: Absolute parent path.
            :param QStandardItemModel|QStandardItem parent: Parent item (or item model, like root of all items).
            """
            dataNames = sorted(
                [
                    data
                    for data
                    in os.listdir(path)
                    if (
                        isdir(join(path, data)) or (
                            isfile(join(path, data)) and
                            not data.endswith((".meta", ".meta.json"))
                        )
                    )
                ]
            )
            for dataName in dataNames:
                dataObject = QStandardItem(dataName)
                dataObject.setEditable(False)
                if isdir(join(path, dataName)):
                    appendNonMeta(join(path, dataName), dataObject)
                parent.appendRow(dataObject)

        if self.rootPath != "": 
            appendNonMeta(self.rootPath, self.metadataEditorPage.model) # Fills tree

            self.metadataEditorPage.setRootPath(self.rootPath)
            self.compilerPage.setRootPath(self.rootPath)

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
	
if __name__ == '__main__':
   main()