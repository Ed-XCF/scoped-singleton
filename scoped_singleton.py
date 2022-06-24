import hashlib
import threading
import contextvars  # noqa
from weakref import WeakValueDictionary
from urllib.parse import quote
from functools import partial
from abc import ABCMeta, abstractmethod
from typing import Type

__all__ = [
    "thread_scoped_singleton",
    "context_scoped_singleton",
]


class Registry(metaclass=ABCMeta):
    @abstractmethod
    def __contains__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError


class ThreadLocalRegistry(Registry):
    def __init__(self):
        self.scope = threading.local()
        self.scope.registry = WeakValueDictionary()

    def __contains__(self, key):
        return key in self.scope.registry

    def __getitem__(self, item):
        return self.scope.registry[item]

    def __setitem__(self, key, value):
        self.scope.registry[key] = value


class ContextVarRegistry(Registry):
    def __init__(self):
        self.scope = contextvars.ContextVar(type(self).__name__)
        self.scope.set(WeakValueDictionary())

    def __contains__(self, key):
        return key in self.scope.get()

    def __getitem__(self, item):
        return self.scope.get()[item]

    def __setitem__(self, key, value):
        self.scope.get()[key] = value


def scoped_singleton(registry_klass: Type[Registry], cls):
    registry = registry_klass()

    def wrap(*args, **kwargs):
        quote_args = [quote(str(i)) for i in args]
        quote_kwargs = [f"{quote(str(k))}={quote(str(v))}" for k, v in kwargs.items()]
        quote_params = ":".join(quote_args + quote_kwargs)
        original_key = ".".join([cls.__module__ or "", cls.__qualname__, quote_params])
        registry_key = hashlib.md5(original_key.encode()).hexdigest()

        if registry_key in registry:
            return registry[registry_key]

        registry[registry_key] = instance = cls(*args, **kwargs)
        return instance

    return wrap


thread_scoped_singleton = partial(scoped_singleton, ThreadLocalRegistry)
context_scoped_singleton = partial(scoped_singleton, ContextVarRegistry)
