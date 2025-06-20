import mutagen
import logging


class MetadataReader:
    def __init__(self):
        pass

    def read_metadata(self, file_path):
        try:
            audio = mutagen.File(file_path)
            if audio is None:
                logging.warning('метаданные не найдены')
                return None

            metadata = {
                'title': self._get_tag(audio, 'title', 'TIT2'),
                'artist': self._get_tag(audio, 'artist', 'TPE1'),
                'album': self._get_tag(audio, 'album', 'TALB'),
                'genre': self._get_tag(audio, 'genre', 'TCON'),
                'year': self._get_tag(audio, 'date', 'TDRC'),
                'track': self._get_tag(audio, 'tracknumber', 'TRCK'),
                'length': self._format_length(
                    audio.info.length if hasattr(audio.info, 'length') else 0
                )
            }
            return metadata
        except Exception as e:
            logging.error(f'ошибка чтения: {e}')
            return None

    def _get_tag(self, audio, tag_name, id3_tag):
        try:
            if hasattr(audio, 'tags'):
                if tag_name in audio.tags:
                    return str(audio.tags[tag_name][0])
                elif id3_tag in audio.tags:
                    return str(audio.tags[id3_tag][0])
            return 'неизвестно'
        except Exception as e:
            logging.error(f'ошибка тега {tag_name}: {e}')
            return 'неизвестно'

    def _format_length(self, seconds):
        try:
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f'{minutes:02d}:{seconds:02d}'
        except Exception as e:
            logging.error(f'ошибка формата: {e}')
            return '00:00'
