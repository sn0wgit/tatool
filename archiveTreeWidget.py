from os.path import join
from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QTreeView, QMessageBox

from metadataEditorWidget import DataInfoWidget

class DataTreeWidget(QTreeView):
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
        # Redefined inherited method
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