from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from os.path import basename

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

if __name__ == "__main__":
    pass