import sys
import os
from os.path import isfile, isdir, join
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QAction, QResizeEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QTabWidget, QFileDialog

from metadataEditor import MetadataEditorTab
from compiler import CompilerTab

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

        self.metadataEditorPage = MetadataEditorTab()
        self.compilerPage = CompilerTab(self.metadataEditorPage)
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