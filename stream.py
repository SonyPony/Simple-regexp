# coding=utf-8

class IStream:
    def __init__(self, text: str):
        self._text = text
        self._pos = 0

    def rewind(self) -> None:
        if self._pos:
            self._pos -= 1

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self._pos >= len(self._text):
            raise StopIteration

        c = self._text[self._pos]
        self._pos += 1
        return c

