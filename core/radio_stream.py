# сделал через ffplay, устанавливал его как хоумбрюшку,
# но в установщик я знаю как его упаковать, я просто возьму сборку для винды
# засуну ее в кор и буду прописать ffplay path при запуске
# https://www.ffmpeg.org/download.html#build-windows ссылка для установки,
# либо я могу скинуть скринкаст или уже версию с установщиком, но мне нужно
# еще потестить на винде, прямо сейчас нет такой возможности
import subprocess
import threading
import time
import logging


class RadioStream:
    def __init__(self):
        self.stream_url = None
        self.is_playing = False
        self.stream_thread = None
        self.stop_event = threading.Event()
        self.process = None

    def load_stream(self, url):
        try:
            self.stream_url = url
            return True
        except Exception as e:
            logging.error(f'ошибка загрузки: {e}')
            return False

    def _stream_audio(self):
        try:
            logging.info(f'загрузка: {self.stream_url}')
            self.process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", self.stream_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            while self.process.poll() is None and not self.stop_event.is_set():
                time.sleep(0.1)

        except Exception as e:
            logging.error(f'ошибка: {e}')
        finally:
            self.is_playing = False

    def play(self):
        if self.stream_url:
            try:
                self.stop_event.clear()
                if self.stream_thread and self.stream_thread.is_alive():
                    self.stop()
                self.stream_thread = threading.Thread(
                    target=self._stream_audio)
                self.stream_thread.daemon = True
                self.stream_thread.start()
                self.is_playing = True
                return True
            except Exception as e:
                logging.error(f'ошибка: {e}')
                return False
        return False

    def stop(self):
        try:
            self.stop_event.set()
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=1)
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=1.0)
            self.is_playing = False
            return True
        except Exception as e:
            logging.error(f'ошибка: {e}')
            return False

    def set_volume(self, volume):
        try:
            if self.process:
                self.stop()
                self.process = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-volume",
                        str(int(volume * 100)), self.stream_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            return True
        except Exception as e:
            logging.error(f'ошибка: {e}')
            return False
