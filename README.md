# pyplayer

музыкальный плеер с радио на python/qt5

## проект также доступен на [гитхабе](https://github.com/mazazyrik/pyplayer)

## функции
- воспроизведение аудиофайлов
- плейлисты
- интернет-радио
- визуализация
- звуковые эффекты

## запуск

### ручной запуск
```bash
python -m venv venv
source venv/bin/activate  # linux/mac
venv\Scripts\activate     # windows
pip install -r requirements.txt
python main.py
```

### сборка exe
```bash
pip install pyinstaller
python build.py
```

## заметки
- на маке собрано и протестировано
- на виндовс не тестировалось
- для радио нужен ffplay в папке core/ можно установить через homebrew 
- либо [скачать с сайта](https://ffmpeg.org/download.html) 