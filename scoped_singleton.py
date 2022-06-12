import hashlib
from weakref import WeakValueDictionary
from urllib.parse import quote


def scoped_singleton(cls):
    _registry = WeakValueDictionary()

    def wrap(*args, **kwargs):
        quote_args = [quote(str(i)) for i in args]
        quote_kwargs = [f"{quote(str(k))}={quote(str(v))}" for k, v in kwargs.items()]
        quote_params = ":".join(quote_args + quote_kwargs)
        original_key = ".".join([cls.__module__ or "", cls.__qualname__, quote_params])
        registry_key = hashlib.md5(original_key.encode()).hexdigest()

        if registry_key in _registry:
            return _registry[registry_key]

        _registry[registry_key] = instance = cls(*args, **kwargs)
        return instance

    return wrap
