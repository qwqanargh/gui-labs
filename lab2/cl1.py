
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class CurrencyModel(QObject):
   
    rubChanged = pyqtSignal(float)
    usdChanged = pyqtSignal(float)
    eurChanged = pyqtSignal(float)
 
    message = pyqtSignal(str)

    def __init__(self, usd_rate=81.50, eur_rate=94.80, parent=None):
        super().__init__(parent)
        self._rub = 0.0               # сумма хранится в рублях
        self._usd_rate = usd_rate     # рублей за 1 доллар
        self._eur_rate = eur_rate     # рублей за 1 евро

  
    def rub(self):
        return self._rub

    def usd(self):
        return self._rub / self._usd_rate

    def eur(self):
        return self._rub / self._eur_rate

  
    @pyqtSlot(float)
    def setRub(self, value):
        self._rub = value
        self._notify(source="rub")

    @pyqtSlot(float)
    def setUsd(self, value):
        self._rub = value * self._usd_rate
        self._notify(source="usd")

    @pyqtSlot(float)
    def setEur(self, value):
        self._rub = value * self._eur_rate
        self._notify(source="eur")


    @pyqtSlot(float)
    def setUsdRate(self, rate):
        if rate > 0:
            self._usd_rate = rate
            self._notify(source="rate")

    @pyqtSlot(float)
    def setEurRate(self, rate):
        if rate > 0:
            self._eur_rate = rate
            self._notify(source="rate")

    def _notify(self, source):
     
        if source != "rub":
            self.rubChanged.emit(self.rub())
        if source != "usd":
            self.usdChanged.emit(self.usd())
        if source != "eur":
            self.eurChanged.emit(self.eur())
        self.message.emit(
            f"{self.rub():.2f} ₽ = {self.usd():.2f} $ = {self.eur():.2f} €"
        )
