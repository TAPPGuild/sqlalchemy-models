# sqlalchemy-models

Data models for a server using [SQLAlchemy](http://www.sqlalchemy.org/), and [json schemas](http://json-schema.org/). Intended to be used with Postges, and there will definitely be issues if you try to use with MySQL.

 * Users w/ Permissions & Settings
 * Wallet models (Debits, Credits, Balances) 

## Installation

To ensure forward compatibility, the best way to install sqlalchemy-models is with make.

`make install`

## JSON Schemas

[alchemyjsonschema](https://github.com/isysd/alchemyjsonschema) can convert the SQLAlchemy orm classes in this package into json schemas. To build the schemas, run:

`make schemas`

This will generate a schema for each table, and write them to  `sqlalchemy_odels/schemas/<tablename>.json`.

## Signature Storage

This package comes with a tool for storing signatures related to the rows in your primary tables. If a row represents a record, then the corresponding signature row will be a signed copy of the same data. This feature can be used in auditing, constructing hash trees, or other proofs.

#### Example signature table for User

| id | data | user_id |
|----|------|-------------------------------|
|  1 | "signed bitjws User1" | 1 |
|  2 | "signed bitjws User4" | 4 |
|  3 | "signed bitjws User7" | 7 |

#### Generate a signature class

The generator is a simple function that takes the declarative to be signed as an argument.

```
from sqlalchemy_login_models import generate_signature_class
from sqlalchemy_login_models.model import User
# this is a declarative class derived from Base, just like User
UserSig = generate_signature_class(User)
```

## Ledger

Convert monetary data types to [ledger-cli](http://ledger-cli.org) entries. This trusted standard in double entry accounting is powerful, and accurate.

```
P 2016/07/10 04:56:21 BTC 770.00000000 USD
P 2016/07/10 04:56:21 USD 0.00129870 BTC
2016/07/10 04:56:21 testx BTC_USD sell
    ;<Trade(trade_id='kraken|SKDFJS-GFSDS-SDFSDF', side='sell', amount=1.10000000 BTC, price=770.00000000 USD, fee=1.00000000 USD, fee_side='quote', market='BTC_USD', exchange='kraken', time=2016/07/10 04:56:21)>
    Assets:kraken:USD    846.00000000 USD @ 0.00129870 BTC
    FX:BTC_USD:sell   -847.00000000 USD @ 0.00129870 BTC
    Assets:kraken:BTC    -1.10000000 BTC @ 770.00000000 USD
    FX:BTC_USD:sell   1.10000000 BTC @ 770.00000000 USD
    Expenses:TradeFee    1.00000000 USD @ 0.00129870 BTC
```
