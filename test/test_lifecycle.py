"""
Static data models don't have much to test, but this is a place to load
the various models and ensure the results are as expected.

Foreign key and complex data types the only things that might go wong. Exercise.
"""
import alchemyjsonschema as ajs
import copy
import json
import pytest
import random
import string
import sqlalchemy as sa
import sqlalchemy.orm as orm
import time
from alchemyjsonschema.dictify import jsonify
from jsonschema import validate
from sqlalchemy_login_models import model as lmodels

factory = ajs.SchemaFactory(ajs.AlsoChildrenWalker)

eng_URI = 'sqlite:////tmp/test.db'
ADDRESS = ''.join([random.choice(string.ascii_letters) for n in xrange(19)])
USER = {'username': ADDRESS[0:8]}
USER_KEY = {'key': ADDRESS, 'keytype': 'public'}
eng = sa.create_engine(eng_URI)
ses = orm.sessionmaker(bind=eng)()
for t in lmodels.__all__:
    getattr(lmodels, t).metadata.create_all(eng)


def test_User():
    user = lmodels.User(**USER)
    ses.add(user)
    ses.commit()
    user_schema = factory.__call__(user)
    print user_schema
    print json.dumps(user_schema, indent=4)
    udict = jsonify(user, user_schema)
    assert validate(udict, user_schema) is None

    USER_KEY['user_id'] = user.id
    ukey = lmodels.UserKey(**USER_KEY)
    ses.add(ukey)
    ses.commit()
    ukey_schema = factory.__call__(ukey)
    ukey_dict = jsonify(ukey, ukey_schema)
    print ukey_schema
    print json.dumps(ukey_schema, indent=4)
    print ukey_dict['createtime']
    assert validate(ukey_dict, ukey_schema) is None

