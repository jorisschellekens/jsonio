import typing
import unittest

from jsonio import JSONIO


class TestAggregation(unittest.TestCase):

    def test_dict_to_json(self):
        a: typing.Dict[str, str] = {"Lorem": "Ipsum",
                                    "Dolor": "Sit",
                                    "Amet": "Consectetur"}
        b: str = JSONIO.obj_to_json(a)
        c: typing.Dict[str, str] = JSONIO.json_to_obj(b)
        assert a == c

    def test_list_to_json(self):
        a: typing.List[str] = ["Lorem", "Ipsum", "Dolor", "Sit", "Amet"]
        b: str = JSONIO.obj_to_json(a)
        c: typing.List[str] = JSONIO.json_to_obj(b)
        assert a == c

    def test_set_to_json(self):
        a: typing.Set[str] = {"Lorem", "Ipsum", "Dolor", "Sit", "Amet"}
        b: str = JSONIO.obj_to_json(a)
        c: typing.Set[str] = JSONIO.json_to_obj(b)
        assert a == c

    def test_tuple_to_json(self):
        a: typing.Tuple[str,str,str] = ("Lorem", "Ipsum", "Dolor")
        b: str = JSONIO.obj_to_json(a)
        c: typing.Tuple[str,str,str] = JSONIO.json_to_obj(b)
        assert a == c

    def test_nested_dict_to_json(self):
        a: typing.Dict[str, typing.Any] = {"Lorem": "Ipsum",
                                    "Dolor": {"Sit": "Sat", "Sat": "Sit"},
                                    "Amet": "Consectetur"}
        b: str = JSONIO.obj_to_json(a)
        c: typing.Dict[str, typing.Any] = JSONIO.json_to_obj(b)
        assert a == c

    def test_nested_list_to_json(self):
        a: typing.List[typing.List[str]] = [["Lorem", "Ipsum"], ["Dolor"], ["Sit", "Amet", "Consectetur"]]
        b: str = JSONIO.obj_to_json(a)
        c: typing.List[typing.List[str]] = JSONIO.json_to_obj(b)
        assert a == c

