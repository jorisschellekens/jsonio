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
    def _get_empty_obj_from_str(fully_quantified_class_path: str) -> typing.Any:
        from importlib import import_module
        try:
            module_path, class_name = fully_quantified_class_path.rsplit('.', 1)
            module = import_module(module_path)
            klass = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(fully_quantified_class_path)

        # overwrite __init__
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
            y_id: int = id(y)
            if y_id in dne:
                continue
            stk.pop(0)

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
        # aggregation types
        #
        if isinstance(x, dict):
            if is_root_object:
                return [{JSONIO._obj_to_json(k, False, xref_id_template, xref):JSONIO._obj_to_json(v, False, xref_id_template, xref) for k,v in x.items()}, xref]
            else:
                xref[xref_id_template % id(x)] = {JSONIO._obj_to_json(k, False, xref_id_template, xref):JSONIO._obj_to_json(v, False, xref_id_template, xref) for k,v in x.items()}
                return xref_id_template % id(x)
        if isinstance(x, list):
            if is_root_object:
                return [[JSONIO._obj_to_json(k, False, xref_id_template, xref) for k in x], xref]
            else:
                xref[xref_id_template % id(x)] = [JSONIO._obj_to_json(k, False, xref_id_template, xref) for k in x]
                return xref_id_template % id(x)
        if isinstance(x, set):
            if is_root_object:
                return [{"__values__": [JSONIO._obj_to_json(k, False, xref_id_template, xref) for k in x], "__class__": "set"}, xref]
            else:
                xref[xref_id_template % id(x)] = {"__values__": [JSONIO._obj_to_json(k, False, xref_id_template, xref) for k in x], "__class__": "set"}
                return xref_id_template % id(x)
        if isinstance(x, tuple):
            if is_root_object:
                return [{"__values__": [JSONIO._obj_to_json(k, False, xref_id_template, xref) for k in x], "__class__": "tuple"}, xref]
            else:
                xref[xref_id_template % id(x)] = {"__values__": [JSONIO._obj_to_json(k, False, xref_id_template, xref) for k in x], "__class__": "tuple"}
                return xref_id_template % id(x)

        #
        # objects
        #
        x_as_dict: typing.Dict[typing.Any, typing.Any] = {}
        for key, value in x.__dict__.items():
            if isinstance(value, types.FunctionType):
                continue
            if isinstance(value, types.MethodType):
                continue
            x_as_dict[JSONIO._obj_to_json(key, False, xref_id_template, xref)] = JSONIO._obj_to_json(value, False, xref_id_template, xref)
        x_as_dict["__class__"] = x.__class__.__module__ + "." + x.__class__.__qualname__
        if is_root_object:
            return [x_as_dict, xref]
        else:
            xref[xref_id_template % id(x)] = x_as_dict
            return xref_id_template % id(x)


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
