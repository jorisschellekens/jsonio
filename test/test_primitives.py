import unittest

from jsonio import JSONIO


class TestPrimitives(unittest.TestCase):

    def test_bool_to_json(self):
        a: bool = True
        b: str = JSONIO.obj_to_json(a)
        c: bool = JSONIO.json_to_obj(b)
        assert a == c

    def test_float_to_json(self):
        a: float = 5.5
        b: str = JSONIO.obj_to_json(a)
        c: float = JSONIO.json_to_obj(b)
        assert a == c

    def test_int_to_json(self):
        a: int = 5
        b: str = JSONIO.obj_to_json(a)
        c: int = JSONIO.json_to_obj(b)
        assert a == c

    def test_str_to_json(self):
        a: str = "Lorem Ipsum Dolor Sit Amet"
        b: str = JSONIO.obj_to_json(a)
        c: str = JSONIO.json_to_obj(b)
        assert a == c

