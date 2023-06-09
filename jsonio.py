import enum
import json
import re
import types
import typing


class JSONIO:

    #
    # CONSTRUCTOR
    #

    #
    # PRIVATE
    #

    @staticmethod
    def _get_class_obj_from_str(fully_quantified_class_path: str) -> typing.Any:
        from importlib import import_module
        try:
            module_path, class_name = fully_quantified_class_path.rsplit('.', 1)
            module = import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(fully_quantified_class_path)

    @staticmethod
    def _get_empty_obj_from_str(fully_quantified_class_path: str) -> typing.Any:

        # overwrite __init__
        klass = JSONIO._get_class_obj_from_str(fully_quantified_class_path)
        prev_init = klass.__init__
        klass.__init__ = lambda x: None

        # make (empty) object
        empty_obj = klass()

        # restore __init__
        klass.__init__ = prev_init

        # return
        return empty_obj

    @staticmethod
    def _get_xref_id_template(x: typing.Any) -> str:
        stk: typing.List[typing.Any] = [x]
        dne: typing.Set[int] = set()
        strs: typing.Set[str] = set()
        while len(stk) > 0:
            y: typing.Any = stk[0]
            stk.pop(0)
            y_id: int = id(y)
            if y_id in dne:
                continue

            dne.add(y_id)

            #
            # primitives
            #
            if isinstance(y, bool) or isinstance(y, float) or isinstance(y, int):
                continue

            #
            # str
            #
            if isinstance(y, str):
                strs.add(y)
                continue

            #
            # aggregation types
            #
            if isinstance(y, dict):
                stk.extend(y.keys())
                stk.extend(y.values())
                continue
            if isinstance(y, list):
                stk.extend(y)
                continue
            if isinstance(y, set):
                stk.extend(y)
                continue
            if isinstance(y, tuple):
                stk.extend(list(y))
                continue

            #
            # object
            #
            try:
                for key, value in y.__dict__.items():
                    if isinstance(value, types.FunctionType):
                        continue
                    if isinstance(value, types.MethodType):
                        continue
                    stk.append(key)
                    stk.append(value)
            except:
                pass

        # find unique prefix
        xref_id_template_pattern = re.compile("::xref\\.(?P<xref_nr>[0-9]+)\\.")
        max_xref_nr: int = 0
        for s in strs:
            m = xref_id_template_pattern.match(s)
            if m:
                try:
                    max_xref_nr = max(int(m.group("xref_nr")), max_xref_nr)
                except:
                    pass
        max_xref_nr += 1

        # return
        return "::xref." + str(max_xref_nr) + ".%d::"

    @staticmethod
    def _json_to_obj(x: typing.Any,
                     is_resolved: typing.Set[str] = set([]),
                     xref: typing.Dict[str, typing.Any] = {}) -> typing.Any:

        #
        # None
        #
        if x is None:
            return None

        #
        # primitive
        #
        if isinstance(x, bool) or isinstance(x, float) or isinstance(x, int):
            return x
        if isinstance(x, str) and x not in xref:
            return x

        #
        # aggregation types
        #
        if isinstance(x, dict) and "__class__" not in x:
            return {JSONIO._json_to_obj(k, is_resolved, xref):JSONIO._json_to_obj(v, is_resolved, xref) for k,v in x.items()}
        if isinstance(x, list):
            return [JSONIO._json_to_obj(k, is_resolved, xref) for k in x]
        if isinstance(x, dict) and "__class__" in x and x["__class__"] == "set":
            assert "__values__" in x
            assert isinstance(x["__values__"], list)
            return set([JSONIO._json_to_obj(k, is_resolved, xref) for k in x["__values__"]])
        if isinstance(x, dict) and "__class__" in x and x["__class__"] == "tuple":
            assert "__values__" in x
            assert isinstance(x["__values__"], list)
            return tuple([JSONIO._json_to_obj(k, is_resolved, xref) for k in x["__values__"]])

        #
        # reference
        #
        if isinstance(x, str) and x in xref:
            if x not in is_resolved:
                is_resolved.add(x)
                xref[x] = JSONIO._json_to_obj(xref[x], is_resolved, xref)
            return xref[x]

        # make an empty skeleton for each object in xref
        assert isinstance(xref, dict)
        assert isinstance(x, dict)
        assert "__class__" in x
        x_as_object: typing.Any = JSONIO._get_empty_obj_from_str(x["__class__"])
        for fn, fv in x.items():
            if fn == "__class__":
                continue
            setattr(x_as_object, fn, JSONIO._json_to_obj(fv, is_resolved, xref))
        return x_as_object

    @staticmethod
    def _obj_to_json(x: typing.Any,
                     is_root_object: bool = True,
                     xref_id_template: str = "",
                     xref: typing.Dict[str, typing.Any] = {}) -> typing.Any:

        #
        # None
        #
        if x is None:
            if is_root_object:
                return [None, {}]
            return None

        #
        # primitive
        #
        if isinstance(x, bool)          \
                or isinstance(x, float) \
                or isinstance(x, int)   \
                or isinstance(x, str):
            if is_root_object:
                return [x, {}]
            else:
                return x

        #
        # recursion
        #
        xref_id:str = xref_id_template % id(x)
        if xref_id in xref:
            return xref_id

        #
        # aggregation types
        #
        if isinstance(x, dict):
            dict_out = {}
            if not is_root_object:
                xref[xref_id] = dict_out
            for k,v in x.items():
                k2 = JSONIO._obj_to_json(k, False, xref_id_template, xref)
                v2 = JSONIO._obj_to_json(v, False, xref_id_template, xref)
                dict_out[k2] = v2
            if is_root_object:
                return [dict_out, xref]
            return xref_id
        if isinstance(x, list):
            list_out = []
            if not is_root_object:
                xref[xref_id] = list_out
            for k in x:
                list_out.append(JSONIO._obj_to_json(k, False, xref_id_template, xref))
            if is_root_object:
                return [list_out, xref]
            return xref_id
        if isinstance(x, set):
            set_out = {"__class__": "set",
                       "__values__": []}
            if not is_root_object:
                xref[xref_id] = set_out
            for k in x:
                set_out["__values__"].append(JSONIO._obj_to_json(k, False, xref_id_template, xref))
            if is_root_object:
                return [set_out, xref]
            return xref_id
        if isinstance(x, tuple):
            tuple_out = {"__class__": "tuple",
                         "__values__": []}
            if not is_root_object:
                xref[xref_id] = tuple_out
            for k in x:
                tuple_out["__values__"].append(JSONIO._obj_to_json(k, False, xref_id_template, xref))
            if is_root_object:
                return [tuple_out, xref]
            return xref_id

        #
        # enums
        #
        if isinstance(x, enum.Enum):
            return {
                "__class__": x.__class__.__module__ + "." + x.__class__.__qualname__,
                "__value__": x.value
            }

        #
        # objects
        #
        x_as_dict: typing.Dict[typing.Any, typing.Any] = {}
        x_as_dict["__class__"] = x.__class__.__module__ + "." + x.__class__.__qualname__
        if not is_root_object:
            xref[xref_id] = x_as_dict
        for fn, fv in x.__dict__.items():
            if isinstance(fv, types.FunctionType):
                continue
            if isinstance(fv, types.MethodType):
                continue
            fn2 = JSONIO._obj_to_json(fn, False, xref_id_template, xref)
            fv2 = JSONIO._obj_to_json(fv, False, xref_id_template, xref)
            x_as_dict[fn2] = fv2
        if is_root_object:
            return [x_as_dict, xref]
        return xref_id


    #
    # PUBLIC
    #

    @staticmethod
    def json_to_obj(s: str):
        x_and_xref = json.loads(s)
        x: typing.Any = x_and_xref[0]
        xref: typing.Dict[str, typing.Any] = x_and_xref[1]
        return JSONIO._json_to_obj(x,
                                   is_resolved=set([]),
                                   xref=xref)

    @staticmethod
    def obj_to_json(x: typing.Any) -> str:
        return json.dumps(JSONIO._obj_to_json(x,
                                              is_root_object=True,
                                              xref_id_template=JSONIO._get_xref_id_template(x),
                                              xref={}
                                              ),
                          indent=4)
