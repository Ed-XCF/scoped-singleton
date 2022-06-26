# scoped-singleton
![GitHub](https://img.shields.io/github/license/Ed-XCF/scoped-singleton)
[![Build Status](https://app.travis-ci.com/Ed-XCF/redis-property.svg?branch=main)](https://app.travis-ci.com/Ed-XCF/scoped-singleton)
[![codecov](https://codecov.io/gh/Ed-XCF/scoped-singleton/branch/main/graph/badge.svg?token=J3HnAigB4J)](undefined)
![PyPI](https://img.shields.io/pypi/v/scoped-singleton)

Easier sharing data between objects

## Installation
```shell
pip3 install scoped-singleton
```

## How to use it
```python
from dataclasses import dataclass

from scoped_singleton import context_scoped_singleton


@context_scoped_singleton
@dataclass
class Account:
    uuid: str
```

use it with cached_property to stop repeated requests

```python
from dataclasses import dataclass

from cached_property import cached_property
from scoped_singleton import context_scoped_singleton


@context_scoped_singleton
@dataclass
class Account:
    uuid: str

    @cached_property
    def credit_limit(self):
        return rpc(self.uuid)["credit_limit"]


@dataclass
class Transaction:
    id: int
    account_uuid: str
    
    @property
    def account(self):
        return Account(uuid=self.account_uuid)

txn1 = Transaction(id=1, account_uuid="123")
txn2 = Transaction(id=2, account_uuid="123")
txn3 = Transaction(id=3, account_uuid="124")

assert txn1.account is txn2.account
assert txn1.account is not txn3.account
```
