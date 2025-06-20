import logging


class Visualization:
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget
        self.plot_widget.setBackground('#2b2b2b')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'амплитуда')
        self.plot_widget.setLabel('bottom', 'время')
        self.curve = self.plot_widget.plot(pen='y')

    def update(self, data):
        try:
            if len(data) > 0:
                self.curve.setData(data)
        except Exception as e:
            logging.error(f'ошибка визуализации: {e}')
