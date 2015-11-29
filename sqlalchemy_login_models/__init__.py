"""
Base declarative and tools for model manipulation.
"""
import re
from sqlalchemy import Column, Sequence, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import as_declarative, declared_attr

__all__ = ['Base', 'generate_signature_class']

@as_declarative()
class Base(object):
    @declared_attr
    def __tablename__(cls):
        """
        A snake-case name for the table.
        """
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', cls.__name__).lower()

    # can be overwritten :)
    id = Column(Integer, Sequence('%s_id_seq' % __tablename__),
                primary_key=True)


def generate_signature_class(cls):
    """
    Generate a declarative model for storing signatures related to the given
    cls parameter.
    
    :param class cls: The declarative model to generate a signature class for.
    :return: The signature class, as a declarative derived from Base.
    """
    return type("%sSigs" % cls.__name__, (Base, ),
                  {'__tablename__': "%s_sigs" % cls.__tablename__,
                   'id': Column(Integer,
                        Sequence('%s_id_seq' % cls.__tablename__),
                        primary_key=True, 
                        doc="primary key"),
                   'data': Column(String(), nullable=False,
                        doc="The signed data"),
                   '%s_id' % cls.__tablename__: Column(Integer,
                        ForeignKey("%s.id" % cls.__tablename__),
                        nullable=False)
             })


