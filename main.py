import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f'ошибка запуска: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
