"""
cl2 — поле ввода суммы с собственным сигналом.

Сигнал valueEdited(float) испускается только при вводе с клавиатуры
(встроенный сигнал textEdited), а программная установка значения
слотом setValue() его не вызывает — поэтому поля, обновляя друг друга,
не зацикливаются.
"""
from PyQt5.QtCore import Qt, QRegularExpression, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QRegularExpressionValidator, QFont
from PyQt5.QtWidgets import QLineEdit


class NumberField(QLineEdit):
    valueEdited = pyqtSignal(float)

    def __init__(self, value=0.0, parent=None):
        super().__init__(parent)
        # только цифры и не более 4 знаков после точки/запятой
        rx = QRegularExpression(r"^\d{0,12}([.,]\d{0,4})?$")
        self.setValidator(QRegularExpressionValidator(rx, self))
        self.setAlignment(Qt.AlignRight)
        self.setMinimumWidth(180)
        self.setFont(QFont("Arial", 13))
        self.setValue(value)
        self.textEdited.connect(self._on_text_edited)

    @pyqtSlot(str)
    def _on_text_edited(self, text):
        text = text.replace(",", ".")
        value = 0.0 if text in ("", ".") else float(text)
        self.valueEdited.emit(value)

    @pyqtSlot(float)
    def setValue(self, value):
        self.setText(f"{value:.2f}")
