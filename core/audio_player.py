import sounddevice as sd
import numpy as np
from pydub import AudioSegment
import threading


class AudioPlayer:
    def __init__(self):
        self.audio = None
        self.stream = None
        self.is_playing = False
        self.volume = 1.0
        self.left_volume = 1.0
        self.right_volume = 1.0
        self.echo_enabled = False
        self.reverb_enabled = False
        self.current_position = 0
        self.audio_data = None
        self.frame_rate = 44100
        self.stop_event = threading.Event()
        self.duration = 0
        self.total_frames = 0

    def load_file(self, file_path):
        try:
            self.audio = AudioSegment.from_file(file_path)
            self.frame_rate = self.audio.frame_rate * 2
            self.current_position = 0
            samples = np.array(self.audio.get_array_of_samples())
            if len(samples.shape) == 1:
                samples = np.column_stack((samples, samples))
            self.audio_data = samples.astype(np.float32)
            max_val = np.max(np.abs(self.audio_data))
            if max_val > 0:
                self.audio_data = self.audio_data / max_val

            self.total_frames = len(self.audio_data)
            self.duration = self.total_frames / self.frame_rate

            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def play(self):
        if self.audio_data is not None and not self.is_playing:
            self.is_playing = True
            self.stop_event.clear()

            def callback(outdata, frames, time, status):
                if status:
                    print(status)
                if not self.is_playing:
                    raise sd.CallbackStop()

                if self.current_position >= self.total_frames:
                    self.is_playing = False
                    raise sd.CallbackStop()

                end = min(self.current_position + frames, self.total_frames)
                chunk = self.audio_data[self.current_position:end]

                if self.echo_enabled:
                    chunk = self.apply_echo(chunk)
                if self.reverb_enabled:
                    chunk = self.apply_reverb(chunk)

                chunk = self.adjust_channel_volume(chunk)

                if len(chunk) == frames:
                    outdata[:] = chunk
                else:
                    outdata[:len(chunk)] = chunk
                    outdata[len(chunk):] = 0

                self.current_position = end

            try:
                self.stream = sd.OutputStream(
                    channels=2,
                    samplerate=self.frame_rate,
                    callback=callback,
                    dtype=np.float32,
                    blocksize=2048
                )
                self.stream.start()
                print(f"Воспроизведение: {self.frame_rate} Гц")
            except Exception as e:
                print(f"Ошибка: {e}")
                self.is_playing = False

    def pause(self):
        if self.is_playing:
            self.is_playing = False
            if self.stream:
                self.stream.stop()
                self.stream.close()

    def stop(self):
        self.is_playing = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.current_position = 0

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))

    def set_channel_volume(self, left_volume, right_volume):
        self.left_volume = max(0.0, min(1.0, left_volume))
        self.right_volume = max(0.0, min(1.0, right_volume))

    def adjust_channel_volume(self, samples):
        samples = np.array(samples)
        if len(samples.shape) == 2:
            samples[:, 0] *= self.left_volume * self.volume
            samples[:, 1] *= self.right_volume * self.volume
        return samples

    def get_audio_data(self):
        if self.audio_data is not None and self.is_playing:
            return (
                self.audio_data[
                    self.current_position:self.current_position + 1000
                ]
            )
        return np.zeros((1000, 2))

    def get_position(self):
        if self.audio_data is not None:
            return self.current_position / self.frame_rate
        return 0

    def set_position(self, position):
        if self.audio_data is not None:
            self.current_position = int(position * self.frame_rate)
            if self.current_position < 0:
                self.current_position = 0
            elif self.current_position >= self.total_frames:
                self.current_position = self.total_frames - 1

    def get_duration(self):
        return self.duration

    def apply_echo(self, samples, delay=0.5, decay=0.5):
        if len(samples) < 2:
            return samples
        echo_samples = np.zeros_like(samples)
        delay_samples = min(int(delay * self.frame_rate), len(samples) - 1)
        echo_samples[delay_samples:] = samples[:-delay_samples] * decay
        return np.clip(samples + echo_samples, -1.0, 1.0)

    def apply_reverb(self, samples, room_size=0.8, damping=0.5):
        if len(samples) < 2:
            return samples
        reverb_samples = np.zeros_like(samples)
        delay_samples = min(int(room_size * self.frame_rate), len(samples) - 1)
        reverb_samples[delay_samples:] = samples[:-delay_samples] * damping
        return np.clip(samples + reverb_samples, -1.0, 1.0)

    def seek_forward(self, seconds=5):
        if self.audio_data is not None:
            self.current_position += int(seconds * self.frame_rate)
            if self.current_position >= self.total_frames:
                self.current_position = self.total_frames - 1
            self.play()

    def seek_backward(self, seconds=5):
        if self.audio_data is not None:
            self.current_position -= int(seconds * self.frame_rate)
            if self.current_position < 0:
                self.current_position = 0
            self.play()
