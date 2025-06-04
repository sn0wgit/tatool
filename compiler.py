import os
import json
import datetime
from os.path import isfile, join
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QPlainTextEdit, QFormLayout, QMessageBox, QCheckBox

from editor import MetadataEditorTab

class CompilerTab(QWidget):
    """Compiler tab"""
    def __init__(self, metadataEditorPage: MetadataEditorTab):
        super().__init__()

        self.output = ""
        self.APP_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
        self.metadataEditorPage = metadataEditorPage


        self.compileButton = QPushButton("Compile!")
        self.compileButton.setDisabled(True)
        self.compileButton.clicked.connect(self.compileButtonHandler)

        self.compileNote = QLabel("Note: it will overwrite all previous data in .meta.json files!")


        self.dumpLogsToggle = QCheckBox()
        self.dumpLogsToggle.setStatusTip("Logs will be saved in program home directory in format YYYY-MM-DD hh-mm-ss.log")

        self.dumpLogsLabel = QLabel("Dump logs to file")
        self.dumpLogsLabel.setStatusTip("Logs will be saved in program home directory in format YYYY-MM-DD hh-mm-ss.log")


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
        logText = str(datetime.datetime.now()).replace(":", "-")[:19]
        for argindx, arg in enumerate(args):
            if argindx != 0:
                logText += " "
            logText += str(arg)

        print(self.output)

        self.output += "\n" + logText
        self.compileLogs.setPlainText(self.output)

    def setRootPath(self, path:str, setDiabled=False):
        """Method for root path updates.

        :param str path: Absolute path to archive root.
        :param bool setDiabled: Sets if "Compile" button will be disabled."""
        self.rootPath = path
        self.compileButton.setDisabled(setDiabled)

    def compileButtonHandler(self) -> None:
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

            elif criticalWarning == QMessageBox.StandardButton.Abort or criticalWarning == QMessageBox.StandardButton.Escape:
                return None
        
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