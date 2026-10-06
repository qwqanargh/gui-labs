
import sys
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QObject, QTimer, QUrl, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickItem

BASE_DIR = Path(__file__).resolve().parent


class Interface(QObject):
   

    
    autosaveChanged = pyqtSignal()
    intervalChanged = pyqtSignal()
    saveDirChanged = pyqtSignal()
    statusChanged = pyqtSignal()
    # сигнал об успешном сохранении: путь к файлу
    saved = pyqtSignal(str)

    MIN_INTERVAL, MAX_INTERVAL = 1, 300  # секунды

    def __init__(self, save_dir, interval=5):
        super().__init__()
        self._canvas = None          
        self._save_dir = Path(save_dir)
        self._interval = interval    
        self._dirty = False          
        self._grab = None            
        self._last_saved = ""
        self._count = 0

        self._timer = QTimer(self)
        self._timer.setInterval(self._interval * 1000)
        self._timer.timeout.connect(self._on_timeout)

    
    @pyqtProperty(bool, notify=autosaveChanged)
    def autosave(self):
        return self._timer.isActive()

    @pyqtProperty(int, notify=intervalChanged)
    def interval(self):
        return self._interval

    @pyqtProperty(str, notify=saveDirChanged)
    def saveDir(self):
        return str(self._save_dir)

    @pyqtProperty(str, notify=statusChanged)
    def lastSaved(self):
        return self._last_saved

    @pyqtProperty(int, notify=statusChanged)
    def savedCount(self):
        return self._count

    @pyqtProperty(bool, notify=statusChanged)
    def dirty(self):
        return self._dirty

    
    def setCanvas(self, item):
        self._canvas = item

    @pyqtSlot()
    def markDirty(self):
        
        if not self._dirty:
            self._dirty = True
            self.statusChanged.emit()

    @pyqtSlot()
    def toggleAutosave(self):
        if self._timer.isActive():
            self._timer.stop()
        else:
            self._timer.start()
        self.autosaveChanged.emit()

    @pyqtSlot(int)
    def changeInterval(self, delta):
        value = max(self.MIN_INTERVAL, min(self.MAX_INTERVAL, self._interval + delta))
        if value != self._interval:
            self._interval = value
            self._timer.setInterval(value * 1000)  
            self.intervalChanged.emit()

    @pyqtSlot()
    def chooseFolder(self):
        folder = QFileDialog.getExistingDirectory(None, "Папка для сохранения рисунков",
                                                  str(self._save_dir))
        if folder:
            self._save_dir = Path(folder)
            self.saveDirChanged.emit()

    @pyqtSlot()
    def saveNow(self):
        
        self._save()

    
    def _on_timeout(self):
        if self._dirty:
            self._save()

    def _save(self):
        if self._canvas is None or self._grab is not None:
            return 
        result = self._canvas.grabToImage()
        if result is None:  
            print("Не удалось получить изображение холста")
            return
        self._dirty = False  
        self._grab = result
        name = datetime.now().strftime("canvas_%Y-%m-%d_%H-%M-%S.png")
        path = self._save_dir / name
        result.ready.connect(lambda: self._write(result, path))

    def _write(self, result, path):
        self._grab = None
        try:
            self._save_dir.mkdir(parents=True, exist_ok=True)
            ok = result.saveToFile(str(path))
        except OSError as e:
            ok = False
            print("Ошибка:", e)
        if ok:
            self._count += 1
            self._last_saved = path.name
            print("Сохранено:", path)
            self.saved.emit(str(path))
        else:
            self._dirty = True  # повторим при следующем срабатывании таймера
            self._last_saved = "ошибка записи: " + path.name
        self.statusChanged.emit()


if __name__ == '__main__':

    
    app = QApplication(sys.argv)

    interface = Interface(BASE_DIR / "saves", interval=5)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)

    
    engine.load(QUrl.fromLocalFile(str(BASE_DIR / "mainWindow.qml")))

    
    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

  
    canvas = engine.rootObjects()[0].findChild(QQuickItem, "canvas")
    interface.setCanvas(canvas)
    interface.toggleAutosave()  

    code = app.exec()
    del engine 
    sys.exit(code)
