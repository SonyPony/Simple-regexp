# coding=utf-8
from enum import Enum, IntEnum
from stream import IStream


class TokenType(Enum):
    UNKNOWN = ";"
    IDENTIFIER = "i"
    META_QUANTIFIER_0_N = "*"
    META_OR = "|"
    LEFT_BRACKET = "("
    RIGHT_BRACKET = ")"
    META_CONCANATE = "+"

class Token:
    def __init__(self, type=TokenType.UNKNOWN, data=""):
        self._type = type
        self._data = data

    def __str__(self):
        return "Token(type={}, data={})".format(self._type.name, self._data)

    @property
    def type(self) -> TokenType:
        return self._type

    @property
    def data(self) -> str:
        return self._data

class Lexer:
    class FSMStates(IntEnum):
        INIT = 0
        IDENTIFIER = 1

    def __init__(self, source=""):
        self._current_state = Lexer.FSMStates.INIT
        self._source = source
        self._source_iterator = IStream(source)
        self._prev = None

    def __iter__(self):
        return self

    def __next__(self) -> Token:
        assert self._current_state == Lexer.FSMStates.INIT
        supported_meta = ("d", )

        c = next(self._source_iterator, None)

        if c == "\\":
            nc = next(self._source_iterator, None)
            if not nc in supported_meta:
                self._source_iterator.rewind()
            else:
                c = "".join(("\\", nc))

        if not c:
            self._prev = c
            raise StopIteration
        elif c in ("*", "|", "(", ")"):
            t = Token(TokenType(c))
        else:
            t = Token(TokenType.IDENTIFIER, c)

        concanation_combs = {
            (TokenType.IDENTIFIER, TokenType.IDENTIFIER), (TokenType.IDENTIFIER, TokenType.LEFT_BRACKET),
            (TokenType.META_QUANTIFIER_0_N, TokenType.LEFT_BRACKET), (TokenType.RIGHT_BRACKET, TokenType.LEFT_BRACKET),
            (TokenType.META_QUANTIFIER_0_N, TokenType.IDENTIFIER), (TokenType.RIGHT_BRACKET, TokenType.IDENTIFIER)
        }

        if (self._prev, t.type) in concanation_combs:
            if "\\" in t.data:
                self._source_iterator.rewind()
            self._prev = TokenType.META_CONCANATE
            self._source_iterator.rewind()
            return Token(TokenType.META_CONCANATE)

        self._prev = t.type
        return t

    @property
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, v: str) -> None:
        self._source = v
        self._source_iterator = IStream(v)