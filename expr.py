# coding=utf-8
from enum import Enum


class ExprTokenType(Enum):
    META_DOLAR = "$"

class ExprPrecedence(Enum):
    SAME = "="
    SHIFT = "<"
    REDUCE = ">"
    NONE = "x"

class Expression:
    def __init__(self, automat):
        self._automat = automat

    @property
    def automat(self) -> str:
        return self._automat
