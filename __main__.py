import sys
from PyQt5.QtWidgets import QApplication
from gui import TranscriberGui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TranscriberGui()
    gui.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window")
