import os
from os.path import isfile, isdir, relpath, abspath, basename, join
import json
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QFileDialog, QFormLayout, QComboBox, QLineEdit, QMessageBox

from objectPreviewWidget import PreviewWidget

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
        self.saveButton.setStatusTip("Apply changes")
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.forceSave)

        self.previewLabel = QLabel("Preview:")
        self.previewButton = QPushButton("Select file...")
        self.previewButton.setStatusTip("Select image for this object")
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
        self.typeSelection.setStatusTip("Select static type of the object")

        self.i18nnameLabel = QLabel("i18nName:")
        self.i18nnameInput = QLineEdit()
        self.i18nnameInput.setStatusTip("Input unique name of object (it will be used as variable name) to connect the object and translations")
        self.i18nnameInput.textChanged.connect(self.i18nNameChangeHandler)
        self.form.addRow(self.i18nnameLabel, self.i18nnameInput)

        self.currentLanguageSelection = QComboBox()
        self.currentLanguageSelection.setStatusTip("Select a language to edit translations of the object in this language")
        self.currentLanguageSelection.currentIndexChanged.connect(self.currentLanguageChangeHandler)
        self.form.addWidget(self.currentLanguageSelection)

        self.nameLabel = QLabel("Name:")
        self.nameInput = QLineEdit()
        self.nameInput.setStatusTip("Object name (used in user language-based the object image)")
        self.nameInput.textChanged.connect(self.nameChangeHandler)
        self.form.addRow(self.nameLabel, self.nameInput)

        self.descLabel = QLabel("Description:")
        self.descInput = QLineEdit()
        self.descInput.setStatusTip("Object description (more detail text about the object used in user language-based image)")
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
