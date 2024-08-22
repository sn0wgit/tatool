import sys
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridLayout")
        self.resize(500, 500)
        self.move(400, 250)
        
        gl = QGridLayout()
        self.setLayout(gl)

        files = QLabel("Files")
        files.setStyleSheet("background-color: red;")
        preview = QLabel("Preview")
        preview.setStyleSheet("background-color: green;")
        data = QLabel("Data")
        data.setStyleSheet("background-color: blue;")

        gl.addWidget(files, 0, 0, 0, 1)
        gl.addWidget(preview, 0, 1)
        gl.addWidget(data, 1, 1)

        print(gl.getItemPosition(1))

def main():
    app = QApplication(sys.argv)

    window = Window()
    window.show()

    app.exec()
	
if __name__ == '__main__':
   main()