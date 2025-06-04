from objectPreviewWidget import PreviewWidget
from metadataEditorWidget import DataInfoWidget
from archiveTreeWidget import DataTreeWidget

from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QWidget, QGridLayout

class MetadataEditorTab(QWidget):
    """Metadata editor tab"""
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)

        self.preview = PreviewWidget()

        self.dataEditor = DataInfoWidget(self.preview)

        self.files = DataTreeWidget(self.dataEditor)
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
