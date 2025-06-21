#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

logger.info("сборка exe")

for folder in ["build", "dist"]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
if os.path.exists("PyPlayer.spec"):
    os.remove("PyPlayer.spec")

command = [
    sys.executable,
    '-m',
    'PyInstaller',
    '--name=PyPlayer',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    'main.py'
]

separator = ';' if platform.system() == "Windows" else ':'
command.append(f'--add-data=cat-headphones.gif{separator}.')

hidden_imports = [
    'PyQt5.sip', 'pydub', 'sounddevice', 'mutagen',
    'pyqtgraph', 'requests', 'numpy', 'json', 'threading'
]
for lib in hidden_imports:
    command.append(f'--hidden-import={lib}')

ffplay_path = ''
if platform.system() == "Windows":
    ffplay_path = os.path.join('core', 'ffplay.exe')
else:
    ffplay_path = os.path.join('core', 'ffplay')

if os.path.exists(ffplay_path):
    command.append(f'--add-binary={ffplay_path}{separator}core')
else:
    logger.warning("ffplay не найден")

try:
    subprocess.check_call(command)
    logger.info("готово")
except FileNotFoundError:
    logger.error("pyinstaller не найден")
except subprocess.CalledProcessError as e:
    logger.error(f"ошибка: {e}")
except Exception as e:
    logger.error(f"ошибка: {e}")
