import json
import os
import logging


class PlaylistManager:
    def __init__(self):
        self.playlists_dir = 'playlists'
        if not os.path.exists(self.playlists_dir):
            os.makedirs(self.playlists_dir)

    def create_playlist(self, name, tracks):
        try:
            playlist_path = os.path.join(self.playlists_dir, f'{name}.json')
            with open(playlist_path, 'w') as f:
                json.dump(tracks, f)
            logging.info(f'плейлист создан: {name}')
            return True
        except Exception as e:
            logging.error(f'ошибка создания: {e}')
            return False

    def load_playlist(self, name):
        try:
            playlist_path = os.path.join(self.playlists_dir, f'{name}.json')
            if os.path.exists(playlist_path):
                with open(playlist_path, 'r') as f:
                    tracks = json.load(f)
                logging.info(f'плейлист загружен: {name}')
                return tracks
            logging.warning(f'плейлист не найден: {name}')
            return []
        except Exception as e:
            logging.error(f'ошибка загрузки: {e}')
            return []

    def delete_playlist(self, name):
        try:
            playlist_path = os.path.join(self.playlists_dir, f'{name}.json')
            if os.path.exists(playlist_path):
                os.remove(playlist_path)
                logging.info(f'плейлист удален: {name}')
                return True
            logging.warning(f'плейлист не найден: {name}')
            return False
        except Exception as e:
            logging.error(f'ошибка удаления: {e}')
            return False
