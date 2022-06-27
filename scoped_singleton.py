import contextvars  # noqa
import hashlib
import threading
from abc import ABCMeta, abstractmethod
from functools import partial
from typing import Type
from urllib.parse import quote
from weakref import WeakValueDictionary

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
        self.registry_factory = WeakValueDictionary

    def __contains__(self, key):
        return key in getattr(self.scope, "registry", {})

    def __getitem__(self, item):
        return getattr(self.scope, "registry", {}).get(item)

    def __setitem__(self, key, value):
        old_registry = getattr(self.scope, "registry", None)
        new_registry = old_registry.copy() if old_registry else self.registry_factory()
        new_registry[key] = value
        self.scope.registry = new_registry


class ContextVarRegistry(Registry):
    def __init__(self):
        self.scope = contextvars.ContextVar(
            type(self).__name__,
            default=WeakValueDictionary(),
        )

    def __contains__(self, key):
        return key in self.scope.get()

    def __getitem__(self, item):
        return self.scope.get()[item]

    def __setitem__(self, key, value):
        new_registry = self.scope.get().copy()
        new_registry[key] = value
        self.scope.set(new_registry)


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
