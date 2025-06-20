import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QListWidget,
    QLabel, QFileDialog, QLineEdit, QCheckBox, QInputDialog, QHBoxLayout,
    QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from core.audio_player import AudioPlayer
from core.playlist_manager import PlaylistManager
from core.metadata_reader import MetadataReader
from core.visualization import Visualization
from core.radio_stream import RadioStream
import pyqtgraph as pg
import json
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('mvp player ww')
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet('''
            QMainWindow {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #48b5f2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #4a4a4a;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3daee9;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QListWidget {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #3daee9;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px;
            }
            QCheckBox {
                color: white;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #3daee9;
                border: 1px solid #4a4a4a;
                border-radius: 3px;
            }
        ''')

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        background_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'cat-headphones.gif')
        if os.path.exists(background_path):
            self.background_label = QLabel(central_widget)
            self.background_label.setGeometry(
                0, 0, self.width(), self.height())
            self.background_movie = QMovie(background_path)
            self.background_movie.setScaledSize(self.size())
            self.background_label.setMovie(self.background_movie)
            self.background_movie.start()

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        controls_frame = QFrame()
        controls_frame.setStyleSheet('''
            QFrame {
                background-color: rgba(43, 43, 43, 180);
                border-radius: 10px;
            }
        ''')
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(15, 15, 15, 15)

        buttons_layout = QHBoxLayout()
        self.play_button = QPushButton('▶ навалить')
        self.pause_button = QPushButton('⏸ пауза')
        self.stop_button = QPushButton('⏹ хватит на сегодня')
        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.stop_button)
        controls_layout.addLayout(buttons_layout)

        seek_layout = QHBoxLayout()
        self.forward_button = QPushButton('⏭ вперёд')
        self.backward_button = QPushButton('⏮ назад')
        self.forward_button.pressed.connect(self.seek_forward)
        self.backward_button.pressed.connect(self.seek_backward)
        seek_layout.addWidget(self.backward_button)
        seek_layout.addWidget(self.forward_button)
        controls_layout.addLayout(seek_layout)

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel('🔊 громкость:'))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        controls_layout.addLayout(volume_layout)

        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel('⏱ позиция:'))
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100000)
        self.position_slider.setValue(0)
        self.position_slider.sliderPressed.connect(self.on_slider_pressed)
        self.position_slider.sliderReleased.connect(self.on_slider_released)
        self.position_slider.valueChanged.connect(self.on_slider_value_changed)
        position_layout.addWidget(self.position_slider)
        controls_layout.addLayout(position_layout)

        self.time_label = QLabel('00:00 / 00:00')
        self.time_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.time_label)

        balance_layout = QHBoxLayout()
        balance_layout.addWidget(QLabel('🔊 левое ухо:'))
        self.left_volume_slider = QSlider(Qt.Horizontal)
        self.left_volume_slider.setRange(0, 100)
        self.left_volume_slider.setValue(100)
        self.left_volume_slider.valueChanged.connect(self.set_channel_volume)
        balance_layout.addWidget(self.left_volume_slider)
        controls_layout.addLayout(balance_layout)

        balance_layout2 = QHBoxLayout()
        balance_layout2.addWidget(QLabel('🔊 правое ухо:'))
        self.right_volume_slider = QSlider(Qt.Horizontal)
        self.right_volume_slider.setRange(0, 100)
        self.right_volume_slider.setValue(100)
        self.right_volume_slider.valueChanged.connect(self.set_channel_volume)
        balance_layout2.addWidget(self.right_volume_slider)
        controls_layout.addLayout(balance_layout2)

        playlist_label = QLabel('📋 плейлист:')
        controls_layout.addWidget(playlist_label)
        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_selected)
        controls_layout.addWidget(self.playlist)

        playlist_buttons = QHBoxLayout()
        self.create_playlist_button = QPushButton('📝 создать плейлист')
        self.edit_playlist_button = QPushButton('📂 открыть плейлист')
        self.delete_playlist_button = QPushButton('🗑 удалить плейлист')
        self.create_playlist_button.clicked.connect(self.create_playlist)
        self.edit_playlist_button.clicked.connect(self.edit_playlist)
        self.delete_playlist_button.clicked.connect(self.delete_playlist)
        playlist_buttons.addWidget(self.create_playlist_button)
        playlist_buttons.addWidget(self.edit_playlist_button)
        playlist_buttons.addWidget(self.delete_playlist_button)
        controls_layout.addLayout(playlist_buttons)

        self.open_button = QPushButton('📂 открыть файл')
        self.open_button.clicked.connect(self.open_file)
        controls_layout.addWidget(self.open_button)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#2b2b2b')
        self.plot_widget.setStyleSheet(
            'border: 1px solid #4a4a4a; border-radius: 4px;')
        controls_layout.addWidget(self.plot_widget)
        self.visualization = Visualization(self.plot_widget)

        radio_layout = QHBoxLayout()
        self.radio_url_input = QLineEdit()
        self.radio_url_input.setPlaceholderText('ссылка на радио')
        self.play_radio_button = QPushButton('📻 навалить радио')
        self.play_radio_button.clicked.connect(self.play_radio)
        radio_layout.addWidget(self.radio_url_input)
        radio_layout.addWidget(self.play_radio_button)
        controls_layout.addLayout(radio_layout)

        effects_layout = QHBoxLayout()
        self.echo_checkbox = QCheckBox('🎵 эхо')
        self.reverb_checkbox = QCheckBox('🎵 реверберация')
        self.echo_checkbox.stateChanged.connect(self.toggle_echo)
        self.reverb_checkbox.stateChanged.connect(self.toggle_reverb)
        effects_layout.addWidget(self.echo_checkbox)
        effects_layout.addWidget(self.reverb_checkbox)
        controls_layout.addLayout(effects_layout)

        self.metadata_label = QLabel('ℹ️ метаданные: Нет')
        self.metadata_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.metadata_label)

        self.radio_url = 'http://chanson.hostingradio.ru:8041/chanson128.mp3'
        self.radio_on = False
        self.radio_play_button = QPushButton('▶ шансон')
        self.radio_stop_button = QPushButton('■ остановить шансон')
        self.radio_play_button.clicked.connect(self.play_radio)
        self.radio_stop_button.clicked.connect(self.stop_radio)
        radio_layout2 = QHBoxLayout()
        radio_layout2.addWidget(self.radio_play_button)
        radio_layout2.addWidget(self.radio_stop_button)
        controls_layout.addLayout(radio_layout2)

        self.radio_url_input.setText(self.radio_url)

        main_layout.addWidget(controls_frame)

        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.start(50)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.timer.start(100)

        self.audio_player = AudioPlayer()
        self.playlist_manager = PlaylistManager()
        self.metadata_reader = MetadataReader()
        self.radio_stream = RadioStream()

        self.load_playlist()
        self.load_settings()

    def play(self):
        self.audio_player.play()

    def pause(self):
        self.audio_player.pause()

    def stop(self):
        self.audio_player.stop()

    def set_volume(self, value):
        self.audio_player.set_volume(value / 100.0)
        self.save_settings()

    def set_channel_volume(self):
        left_volume = self.left_volume_slider.value() / 100.0
        right_volume = self.right_volume_slider.value() / 100.0
        self.audio_player.set_channel_volume(left_volume, right_volume)
        self.save_settings()

    def load_playlist(self):
        tracks = self.playlist_manager.load_playlist('default')
        for track in tracks:
            self.playlist.addItem(track)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'открыть аудиофайл', '', 'аудиофайлы ( .mp3  .wav  .flac)')
        if file_path:
            if self.audio_player.load_file(file_path):
                self.playlist.addItem(file_path)
                self.playlist_manager.create_playlist(
                    'default',
                    [self.playlist.item(i).text()
                     for i in range(self.playlist.count())]
                )
                self.update_metadata(file_path)
                duration = self.audio_player.get_duration()
                self.position_slider.setRange(0, int(duration))
                self.position_slider.setValue(0)
                self.time_label.setText(
                    f'00:00 / {self.format_time(duration)}')

    def play_selected(self, item):
        file_path = item.text()
        if self.audio_player.load_file(file_path):
            duration = self.audio_player.get_duration()
            self.position_slider.setRange(0, int(duration))
            self.position_slider.setValue(0)
            self.time_label.setText(f'00:00 / {self.format_time(duration)}')
            self.audio_player.play()
            self.update_metadata(file_path)

    def update_visualization(self):
        if self.audio_player.is_playing:
            data = self.audio_player.get_audio_data()
            self.visualization.update(data)

    def play_radio(self):
        try:
            if not self.radio_on:
                logging.info(f'попытка воспроизведения {self.radio_url}')
                if self.radio_stream.load_stream(self.radio_url):
                    logging.info('воспроизведение радио')
                    if self.radio_stream.play():
                        self.radio_on = True
                        self.metadata_label.setText('шансон')
                    else:
                        logging.critical('ошибка запуска радио')
                else:
                    logging.critical('ошибка загрузки радио')
        except Exception as e:
            logging.critical(f'ошибка воспроизведения радио: {e}')

    def stop_radio(self):
        try:
            if self.radio_on:
                if self.radio_stream.stop():
                    self.radio_on = False
                    self.metadata_label.setText('Радио остановлено')
                else:
                    logging.critical('ошибка остановки радио')
        except Exception as e:
            logging.critical(f'ошибка остановки радио: {e}')

    def toggle_echo(self, state):
        self.audio_player.echo_enabled = state == Qt.Checked
        self.save_settings()

    def toggle_reverb(self, state):
        self.audio_player.reverb_enabled = state == Qt.Checked
        self.save_settings()

    def seek_forward(self):
        self.audio_player.seek_forward()

    def seek_backward(self):
        self.audio_player.seek_backward()

    def update_metadata(self, file_path):
        metadata = self.metadata_reader.read_metadata(file_path)
        if metadata:
            self.metadata_label.setText(
                f'Метаданные: {metadata["title"]} - {metadata["artist"]} - '
                f'{metadata["album"]} - {metadata["genre"]}'
            )
        else:
            self.metadata_label.setText('Метаданные: Нет')

    def create_playlist(self):
        name, ok = QInputDialog.getText(
            self, 'Создать плейлист', 'Введите имя плейлиста:')
        if ok and name:
            self.playlist_manager.create_playlist(
                name,
                [self.playlist.item(i).text()
                 for i in range(self.playlist.count())]
            )

    def edit_playlist(self):
        name, ok = QInputDialog.getText(
            self, 'Открыть плейлист', 'Введите имя плейлиста:')
        if ok and name:
            tracks = self.playlist_manager.load_playlist(name)
            self.playlist.clear()
            for track in tracks:
                self.playlist.addItem(track)

    def delete_playlist(self):
        name, ok = QInputDialog.getText(
            self, 'Удалить плейлист', 'Введите имя плейлиста:')
        if ok and name:
            self.playlist_manager.delete_playlist(name)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.volume_slider.setValue(
                    int(settings.get('volume', 50) * 100))
                self.left_volume_slider.setValue(
                    int(settings.get('left_volume', 100) * 100))
                self.right_volume_slider.setValue(
                    int(settings.get('right_volume', 100) * 100))
                self.echo_checkbox.setChecked(
                    settings.get('echo_enabled', False))
                self.reverb_checkbox.setChecked(
                    settings.get('reverb_enabled', False))
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            'volume': self.volume_slider.value() / 100.0,
            'left_volume': self.left_volume_slider.value() / 100.0,
            'right_volume': self.right_volume_slider.value() / 100.0,
            'echo_enabled': self.echo_checkbox.isChecked(),
            'reverb_enabled': self.reverb_checkbox.isChecked()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f'{minutes:02d}:{seconds:02d}'

    def on_slider_pressed(self):
        self.position_timer.stop()

    def on_slider_released(self):
        self.set_position(self.position_slider.value())
        self.position_timer.start()

    def on_slider_value_changed(self, value):
        if not self.position_slider.isSliderDown():
            return
        duration = self.audio_player.get_duration()
        if duration > 0:
            position = value
            current_time = self.format_time(position)
            total_time = self.format_time(duration)
            self.time_label.setText(f'{current_time} / {total_time}')

    def set_position(self, value):
        if self.audio_player.audio_data is not None:
            duration = self.audio_player.get_duration()
            if duration > 0:
                position = value
                self.audio_player.set_position(position)
                if not self.audio_player.is_playing:
                    self.audio_player.play()

    def update_position(self):
        if self.audio_player.audio_data is not None and (
            self.audio_player.is_playing
        ):
            position = self.audio_player.get_position()
            duration = self.audio_player.get_duration()
            if duration > 0:
                value = int(position)
                if not self.position_slider.isSliderDown():
                    self.position_slider.setValue(value)
                current_time = self.format_time(position)
                total_time = self.format_time(duration)
                self.time_label.setText(f'{current_time} / {total_time}')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'background_movie'):
            self.background_movie.setScaledSize(self.size())
            if hasattr(self, 'background_label'):
                self.background_label.setGeometry(
                    0, 0, self.width(), self.height())
