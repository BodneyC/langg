# Stolen from:
#  https://stackoverflow.com/questions/50490856/creating-a-namespace-with-a-dict-of-dicts

from functools import singledispatch
from types import SimpleNamespace


@singledispatch
def wrap_namespace(ob):
    return ob


@wrap_namespace.register(dict)
def _wrap_dict(ob):
    return SimpleNamespace(**{k: wrap_namespace(v) for k, v in ob.items()})


@wrap_namespace.register(list)
def _wrap_list(ob):
    return [wrap_namespace(v) for v in ob]
