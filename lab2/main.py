
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QFormLayout, QHBoxLayout, QVBoxLayout, QGroupBox,
)

import cl1
import cl2


class Data:
   
    def __init__(self):
        self.myData = {"rub": 1000.0, "usd_rate": 81.50, "eur_rate": 94.80}

    def getData(self):
        return self.myData


def with_unit(field, unit_text):
   
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.addWidget(field)
    lbl = QLabel(unit_text)
    lbl.setMinimumWidth(20)
    lbl.setFont(QFont("Arial", 13))
    h.addWidget(lbl)
    return w


class Some(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР2 — сигналы и слоты: конвертер валют")
        self.data = Data().getData()

       
        self.model = cl1.CurrencyModel(self.data["usd_rate"], self.data["eur_rate"], self)
        m = self.model

        
        self.rub = cl2.NumberField(self.data["rub"])
        self.usd = cl2.NumberField()
        self.eur = cl2.NumberField()
        self.usd_rate = cl2.NumberField(self.data["usd_rate"])
        self.eur_rate = cl2.NumberField(self.data["eur_rate"])

      
        self.rub.valueEdited.connect(m.setRub)
        self.usd.valueEdited.connect(m.setUsd)
        self.eur.valueEdited.connect(m.setEur)
        self.usd_rate.valueEdited.connect(m.setUsdRate)
        self.eur_rate.valueEdited.connect(m.setEurRate)
        
        m.rubChanged.connect(self.rub.setValue)
        m.usdChanged.connect(self.usd.setValue)
        m.eurChanged.connect(self.eur.setValue)
        # модель -> строка состояния (встроенный слот)
        m.message.connect(self.statusBar().showMessage)

       
        sums = QGroupBox("Сумма")
        f1 = QFormLayout(sums)
        f1.addRow("Рубли:", with_unit(self.rub, "₽"))
        f1.addRow("Доллары:", with_unit(self.usd, "$"))
        f1.addRow("Евро:", with_unit(self.eur, "€"))

        rates = QGroupBox("Курс (рублей за 1 единицу валюты)")
        f2 = QFormLayout(rates)
        f2.addRow("1 $ =", with_unit(self.usd_rate, "₽"))
        f2.addRow("1 € =", with_unit(self.eur_rate, "₽"))

        reset = QPushButton("Сбросить")
        reset.clicked.connect(self.reset)

        page = QWidget()
        v = QVBoxLayout(page)
        v.addWidget(sums)
        v.addWidget(rates)
        v.addWidget(reset, alignment=Qt.AlignRight)
        v.addStretch()
        self.setCentralWidget(page)

        m.setRub(self.data["rub"])  
        self.resize(460, 360)

    def reset(self):
 
        d = self.data
        self.usd_rate.setValue(d["usd_rate"])
        self.eur_rate.setValue(d["eur_rate"])
        self.model.setUsdRate(d["usd_rate"])
        self.model.setEurRate(d["eur_rate"])
        self.rub.setValue(d["rub"])
        self.model.setRub(d["rub"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Some()
    window.show()
    sys.exit(app.exec_())
