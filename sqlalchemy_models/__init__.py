"""
Base declarative and tools for model manipulation.
"""
import copy
import datetime
import json
import os
import re
from ledger import Amount

import sqlalchemy as sa
import sqlalchemy.orm as orm
from alchemyjsonschema.dictify import jsonify
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.types import TypeDecorator, FLOAT

__all__ = ['sa', 'orm', 'Base', 'generate_signature_class',
           'LedgerAmount', 'create_session_engine', 'setup_database']


class LedgerAmount(TypeDecorator):
    """
    Represents a ledger amount. A decorated commodity value of high precision.
    Does not preserve commodity, price, or other meta data.

    Usage::
        LedgerAmount()
    """

    @property
    def python_type(self):
        return Amount

    impl = FLOAT

    def process_bind_param(self, value, dialect):
        if value is not None and hasattr(value, 'to_double'):
            value = float(value.to_double())
        return value

    def process_result_value(self, value, dialect):
        if value is not None and not isinstance(value, Amount):
            value = Amount("{0:.8f}".format(float(value)))
        return value


@as_declarative()
class Base(object):
    """
    A Base for SQLAlchemy ORM objects. Automatically fills in id and table.
    """

    @declared_attr
    def __tablename__(self):
        """
        A snake-case name for the table.
        """
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', self.__name__).lower()

    # can be overwritten :)
    id = sa.Column(sa.Integer, sa.Sequence('%s_id_seq' % __tablename__),
                   primary_key=True)


def generate_signature_class(cls):
    """
    Generate a declarative model for storing signatures related to the given
    cls parameter.

    :param class cls: The declarative model to generate a signature class for.
    :return: The signature class, as a declarative derived from Base.
    """
    return type("%sSigs" % cls.__name__, (Base,),
                {'__tablename__': "%s_sigs" % cls.__tablename__,
                 'id': sa.Column(sa.Integer,
                                 sa.Sequence('%s_id_seq' % cls.__tablename__),
                                 primary_key=True,
                                 doc="primary key"),
                 'data': sa.Column(sa.Text(), nullable=False,
                                   doc="The signed data"),
                 '%s_id' % cls.__tablename__: sa.Column(sa.Integer,
                                                        sa.ForeignKey("%s.id" % cls.__tablename__),
                                                        nullable=False)})


def create_session_engine(uri=None, cfg=None):
    """
    Create an sqlalchemy session and engine.

    :param str uri: The database URI to connect to
    :param cfg: The configuration object with database URI info.
    :return: The session and the engine as a list (in that order)
    """
    if uri is not None:
        eng = sa.create_engine(uri)
    elif cfg is not None:
        eng = sa.create_engine(cfg.get('db', 'SA_ENGINE_URI'))
    else:
        raise IOError("unable to connect to SQL database")
    ses = orm.sessionmaker(bind=eng)()
    return ses, eng


def setup_database(eng, modules=None, models=None):
    """
    Set up databases using create_all().

    :param eng: The sqlalchemy engine to use.
    :param list modules: A list of modules with models inside.
    :param list models:  A list of models to setup.
    """
    if modules is not None:
        for modu in modules:
            for m in modu.__all__:
                getattr(modu, m).metadata.create_all(eng)
    if models is not None:
        for mod in models:
            mod.metadata.create_all(eng)


def get_schemas():
    fpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'definitions.json')
    schemas = ""
    for line in open(fpath, 'r'):
        schemas += line
    return json.loads(schemas)['definitions']


def jsonify2(obj, name):
    # TODO replace this with a cached definitions patch
    # this is inefficient to do each time...
    schemas = get_schemas()
    spec = copy.copy(schemas[name])
    spec['definitions'] = schemas
    for attr in obj.__dict__:
        if isinstance(getattr(obj, attr), Amount):
            setattr(obj, attr, getattr(obj, attr).to_double())
    return json.dumps(jsonify(obj, spec))
