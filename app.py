import sys
import os
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QTabWidget, QWidget, QPushButton, QVBoxLayout, QGridLayout, QLabel, QPlainTextEdit, QTreeView, QFileDialog

OUTPUT = """"/items/en.meta.json" created!
"/items/ru.meta.json" created!
Current directory: /items/Balls/
"/items/Balls/arrangement.meta.json" created!
"/items/Balls/en.meta.json" created!
"/items/Balls/ru.meta.json" created!
Current directory: /items/Balls/Default/
Current directory: /items/Balls/Easter/
Current directory: /items/Drones/
"/items/Drones/arrangement.meta.json" created!
"/items/Drones/en.meta.json" created!
"/items/Drones/ru.meta.json" created!
Current directory: /items/Drones/Kargo/
Current directory: /items/Flags/
Current directory: /items/Flags/Default/
Current directory: /items/Meteorites/
Current directory: /items/Meteorites/Christmas Three/
Current directory: /items/Meteorites/Meteorite/
Current directory: /items/Meteorites/Rocket/
Current directory: /items/Mines/
Current directory: /items/Mines/Default [Old 1]/
Current directory: /items/Mines/Default [Old 2]/
Current directory: /items/Mines/Default [Old 3]/
Current directory: /items/Mines/NY/
Current directory: /items/Overdrives/
"/items/Overdrives/arrangement.meta.json" created!
"/items/Overdrives/en.meta.json" created!
"/items/Overdrives/ru.meta.json" created!
Current directory: /items/Overdrives/Bomb/
Current directory: /items/Overdrives/Generator/
Current directory: /items/Overdrives/Icicle/"""

class DataEditorPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)

        files = QTreeView()
        files.setMaximumWidth(380)
        preview = QLabel("Preview")
        preview.setStyleSheet("border: 1px solid rgba(255,255,255,0.25);")
        data = QLabel("Data")
        data.setStyleSheet("border: 1px solid rgba(255,255,255,0.25);")

        layout.addWidget(files, 0, 0, 0, 1)
        layout.addWidget(preview, 0, 1)
        layout.addWidget(data, 1, 1)

class CompilerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.compileButton = QPushButton("Compile!")
        self.compileNote = QLabel("Note: it will overwrite all previous data in .meta.json files!")
        self.compileLogs = QPlainTextEdit(OUTPUT)
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
        print(self.rootPath)

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
	
if __name__ == '__main__':
   main()