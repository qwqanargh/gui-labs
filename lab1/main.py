
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QRegion, QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
)

ASSETS = Path(__file__).resolve().parent / "assets"
LABEL_TEXT = "Привет! Нажми «Кнопку 1»"
NORMAL_SIZE = (540, 340)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР1 — окно, надпись и кнопки")

        # ресурсы
        self.picture = QPixmap(str(ASSETS / "picture.png"))
        self.shape = QPixmap(str(ASSETS / "shape.png"))

        # состояние
        self.show_picture = False   
        self.shaped = False         
        self._drag_offset = None    

        
        self.label = QLabel(LABEL_TEXT)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(240, 140)
        self.label.setFont(QFont("Arial", 14))

        self.btn1 = QPushButton("Кнопка 1")
        self.btn1.setToolTip("Заменить надпись на изображение")
        self.btn2 = QPushButton("Кнопка 2")
        self.btn2.setToolTip("Изменить форму окна (полупрозрачный PNG)")
        for b in (self.btn1, self.btn2):
            b.setMinimumSize(110, 34)
            b.setCursor(Qt.PointingHandCursor)

        
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.btn1)
        buttons.addSpacing(30)
        buttons.addWidget(self.btn2)
        buttons.addStretch()

        self.layout_ = QVBoxLayout(self)
        self.layout_.addStretch()
        self.layout_.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layout_.addSpacing(16)
        self.layout_.addLayout(buttons)
        self.layout_.addStretch()

        # --- сигналы и слоты ---
        self.btn1.clicked.connect(self.toggle_label)
        self.btn2.clicked.connect(self.toggle_shape)

        self.resize(*NORMAL_SIZE)


    def toggle_label(self):
        """Надпись <-> изображение."""
        self.show_picture = not self.show_picture
        if self.show_picture:
            self.label.setPixmap(self.picture)
            self.btn1.setToolTip("Вернуть текстовую надпись")
        else:
            self.label.setPixmap(QPixmap())
            self.label.setText(LABEL_TEXT)
            self.btn1.setToolTip("Заменить надпись на изображение")

  
    def toggle_shape(self):
        """Обычное окно <-> окно в форме полупрозрачного PNG."""
        self.shaped = not self.shaped
        pos = self.pos()
        if self.shaped:
            # окно без рамки с прозрачным фоном; форму задаёт PNG
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.setFixedSize(self.shape.size())
           
            self.setMask(QRegion(self.shape.mask()))
            self.layout_.setContentsMargins(70, 70, 70, 70)
            self.label.setStyleSheet("color: white;")
            self.setStyleSheet(
                "QPushButton { background: rgba(255,255,255,200); border-radius: 8px;"
                " padding: 6px 12px; } QPushButton:hover { background: white; }"
                " QToolTip { color: black; background: white; }"
            )
        else:
            self.clearMask()
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.setWindowFlags(Qt.Window)
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.resize(*NORMAL_SIZE)
            self.layout_.setContentsMargins(11, 11, 11, 11)
            self.label.setStyleSheet("")
            self.setStyleSheet("")
        self.move(pos)
        self.show()  

    def paintEvent(self, event):
        if self.shaped:
            p = QPainter(self)
            p.setCompositionMode(QPainter.CompositionMode_Source)
            p.fillRect(self.rect(), Qt.transparent)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
            p.drawPixmap(0, 0, self.shape)
        super().paintEvent(event)

   
    def mousePressEvent(self, e):
        if self.shaped and e.button() == Qt.LeftButton:
            self._drag_offset = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.shaped and self._drag_offset is not None:
            self.move(e.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, e):
        self._drag_offset = None

    def keyPressEvent(self, e):
        
        if e.key() == Qt.Key_Escape:
            self.close()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
