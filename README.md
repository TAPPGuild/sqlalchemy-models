# sqlalchemy-login-models

User related data models for a server using [SQLAlchemy](http://www.sqlalchemy.org/), and [json schemas](http://json-schema.org/).

 * User class
 * User Permissions
 * User Settings

# Installation

To ensure forward compatibility, the best way to install sqlalchemy-login-models is with make.

`make install`

# JSON Schemas

[alchemyjsonschema](https://github.com/isysd/alchemyjsonschema) can convert the SQLAlchemy orm classes in this package into json schemas. To build the schemas, run:

`make schemas`

This will generate a schema for each table, and write them to  `sqlalchemy_login_models/schemas/<tablename>.json`.


