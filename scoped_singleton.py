import hashlib
import threading
from abc import ABCMeta, abstractmethod
from functools import partial
from typing import Type
from urllib.parse import quote
from weakref import WeakValueDictionary

__all__ = [
    "thread_scoped_singleton",
]


class Registry(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError


class ThreadLocalRegistry(Registry):
    def __init__(self, _):
        self.registry = threading.local()

    def __getitem__(self, item):
        ident = threading.current_thread().ident
        return getattr(self.registry, ident)[item]

    def __setitem__(self, item, value):
        ident = threading.current_thread().ident
        if not hasattr(self.registry, ident):
            setattr(self.registry, ident, WeakValueDictionary())

        getattr(self.registry, ident)[item] = value


def scoped_singleton(registry_klass: Type[Registry], cls):
    registry = registry_klass(cls.__name__)

    def wrap(*args, **kwargs):
        quote_args = [quote(str(i)) for i in args]
        quote_kwargs = [f"{quote(str(k))}={quote(str(v))}" for k, v in kwargs.items()]
        quote_params = ":".join(quote_args + quote_kwargs)
        original_key = ".".join([cls.__module__ or "", cls.__qualname__, quote_params])
        registry_key = hashlib.md5(original_key.encode()).hexdigest()

        try:
            return registry[registry_key]
        except (AttributeError, KeyError):
            instance = registry[registry_key] = cls(*args, **kwargs)
            return instance

    return wrap


thread_scoped_singleton = partial(scoped_singleton, ThreadLocalRegistry)
