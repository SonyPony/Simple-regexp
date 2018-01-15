# coding=utf-8
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QLabel, QPushButton,
                             QRadioButton, QVBoxLayout, QGroupBox)

from fa_generator import FiniteAutomat
from expr_parser import Parser

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._match_whole_mode = QRadioButton("Celé", self)
        self._match_whole_mode.setChecked(True)
        self._match_substring_mode = QRadioButton("Sub string", self)
        self._input = QLineEdit()
        self._input.setPlaceholderText("Kontrolovaný text")
        self._re_input = QLineEdit()
        self._re_input.setPlaceholderText("Regulární výraz")

        self._output = QLabel()
        self._check_button = QPushButton("Kontrola", self)

        layout = QVBoxLayout()
        layout.addWidget(self._match_whole_mode)
        layout.addWidget(self._match_substring_mode)
        layout.addWidget(self._re_input)
        layout.addWidget(self._input)
        layout.addWidget(self._output)
        layout.addWidget(self._check_button)

        self.setLayout(layout)

        self._check_button.clicked.connect(self.check)

    def check(self):
        try:
            p = Parser(self._re_input.text())
            ka = p.parse()
            if not ka:
                self._output.setText("Syntax error.")
                return

            dka = ka.dka()
            if self._match_whole_mode.isChecked():
                res = dka.eval(self._input.text(), FiniteAutomat.MatchMode.MATCH_WHOLE)
                if res:
                    self._output.setText("Shoda")
                else:
                    self._output.setText("Neshoda")
            elif self._match_substring_mode.isChecked():
                res = dka.eval(self._input.text(), FiniteAutomat.MatchMode.MATCH_SUB)
                if res is False:
                    self._output.setText("Řetězec nenalezen")
                else:
                    self._output.setText("Řetězec nalezen na pozici {}".format(res))
        except Exception as e:
            print(e)

"""app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())"""

p = Parser("6\\da")

a = p.parse()
print(a.start)
print(a.end)
print(a._graph)
a = a.dka()
print(a._start_is_end)
print(a._graph)
print("starte")
a.eval("67a", FiniteAutomat.MatchMode.MATCH_WHOLE)



