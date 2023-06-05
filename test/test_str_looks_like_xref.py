import typing
import unittest

from jsonio import JSONIO


class TestStrLooksLikeXRef(unittest.TestCase):

   def test_str_looks_like_xref(self):
       a: typing.Dict[typing.Tuple[str, str], str] = {("Lorem", "Ipsum"):"::xref.2.0::",
                                                      ("Dolor", "Sit"): "::xref.1.0::",
                                                      ("Amet", "Nunc"): "::xref.3.0::",
                                                }
       b: str = JSONIO.obj_to_json(a)
       c: typing.Dict[typing.Tuple[str, str], str] = JSONIO.json_to_obj(b)
       assert "::xref.4." in b
       assert a == c

