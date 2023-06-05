import typing
import unittest

from jsonio import JSONIO


class TestNone(unittest.TestCase):

    def test_none(self):
        a: typing.Optional[int] = None
        b: str = JSONIO.obj_to_json(a)
        c: typing.Optional[int] = JSONIO.json_to_obj(b)
        assert a == c

    def test_list_containing_none(self):
        a: typing.List[typing.Union[int, None]] = [1, 2, 3, None, 5]
        b: str = JSONIO.obj_to_json(a)
        c: typing.List[typing.Union[int, None]] = JSONIO.json_to_obj(b)
        assert a == c

    def test_dict_containing_none(self):
        a: typing.Dict[str, typing.Optional[str]] = {"Lorem": "Ipsum",
                                                     "Dolor": None,
                                                     "Sit": "Amet"}
        b: str = JSONIO.obj_to_json(a)
        c: typing.Dict[str, typing.Optional[str]] = JSONIO.json_to_obj(b)
        assert a == c
