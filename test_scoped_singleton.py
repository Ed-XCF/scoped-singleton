import gc
from dataclasses import dataclass

from scoped_singleton import scoped_singleton


@scoped_singleton
@dataclass
class Account:
    uuid: str


def test_scoped_singleton():
    gc.collect()
    a, b, c = Account(uuid="123"), Account(uuid="123"), Account(uuid="124")
    assert a is b
    assert a is not c
    assert b is not c
    del a
    gc.collect()
    d = Account(uuid="123")
    assert d is b
    assert d is not c
    id_d = id(d)
    del b, d
    gc.collect()
    e, f = Account(uuid="456"), Account(uuid="123")
    # f = Account(uuid="123")
    assert f is not c
    id_f = id(f)
    assert id_f != id_d
