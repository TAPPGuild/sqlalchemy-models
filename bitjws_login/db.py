"""
Database access via SQLAlchemy and helper functions.
"""
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

SABase = declarative_base()

__all__ = ['SABase', 'dictify_obj', 'query_to_obj']


def dictify_obj(obj, cls):
    """
    Convert an SQLAlchemy object into a dictionary.

    :param SABase obj: The object to dictify
    :param class cls: The object's class
    """
    columns = [c.name for c in c.__table__.columns]
    columnobjs = dict([(c, getattr(obj, c)) for c in columns])
    return columnobjs


def query_to_obj(query, cls):
    """
    Convert an SQLAlchemy object into a dictionary.
    """
    if isinstance(query, SABase):
        return dictify_item(query, cls)
    else:
        objs = []
        for obj in query:
            objs.append(dictify_item(obj, cls))
        return objs

