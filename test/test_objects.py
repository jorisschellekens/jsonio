import unittest

from jsonio import JSONIO

class Point:

    def __init__(self, x: int, y: int):
        self._x: int = x
        self._y: int = y

    def get_x(self) -> int:
        return self._x

    def get_y(self) -> int:
        return self._y


class Line:

    def __init__(self, p0: Point, p1: Point):
        self._p0: Point = p0
        self._p1: Point = p1

    def __len__(self):
        return ((self._p0.get_x() - self._p1.get_x()) ** 2 + (self._p0.get_y() - self._p1.get_y()) ** 2) ** 0.5


class TestPrimitives(unittest.TestCase):

    def test_point_to_json(self):
        a: bool = True
        b: str = JSONIO.obj_to_json(a)
        c: bool = JSONIO.json_to_obj(b)
        assert a == c

    def test_dict_of_point_to_json(self):
        a: float = 5.5
        b: str = JSONIO.obj_to_json(a)
        c: float = JSONIO.json_to_obj(b)
        assert a == c

    def test_list_of_point_to_json(self):
        a: int = 5
        b: str = JSONIO.obj_to_json(a)
        c: int = JSONIO.json_to_obj(b)
        assert a == c

    def test_line_to_json(self):
        a: str = "Lorem Ipsum Dolor Sit Amet"
        b: str = JSONIO.obj_to_json(a)
        c: str = JSONIO.json_to_obj(b)
        assert a == c

    def test_dict_of_line_to_json(self):
        pass

    def test_list_of_line_to_json(self):
        pass