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
from sqlalchemy_login_models import generate_signature_class, Base, model as lmodels

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
    user_schema = factory.__call__(lmodels.User)
    #print user_schema
    #print json.dumps(user_schema, indent=4)
    udict = jsonify(user, user_schema)
    assert validate(udict, user_schema) is None

    USER_KEY['user_id'] = user.id
    ukey = lmodels.UserKey(**USER_KEY)
    ses.add(ukey)
    ses.commit()
    ukey_schema = factory.__call__(lmodels.UserKey)
    ukey_dict = jsonify(ukey, ukey_schema)
    #print ukey_schema
    del ukey_dict['user']
    #print json.dumps(ukey_schema, indent=4)
    assert validate(ukey_dict, ukey_schema) is None


def test_names():
    assert lmodels.User.__name__ == 'User'
    assert lmodels.User.__tablename__ == 'user'
    assert lmodels.UserKey.__name__ == 'UserKey'
    assert lmodels.UserKey.__tablename__ == 'user_key'

def test_signature_class():
    sigclass = generate_signature_class(lmodels.User)
    assert hasattr(sigclass, 'data')
    assert hasattr(sigclass, 'id')
    assert hasattr(sigclass, '%s_id' % 'user')
    assert sigclass.__name__ == 'UserSigs'
    assert sigclass.__tablename__ == 'user_sigs'
    sigkeyclass = generate_signature_class(lmodels.UserKey)
    assert hasattr(sigkeyclass, 'data')
    assert hasattr(sigkeyclass, 'id')
    assert hasattr(sigkeyclass, '%s_id' % 'user_key')
    assert sigkeyclass.__name__ == 'UserKeySigs'
    assert sigkeyclass.__tablename__ == 'user_key_sigs'

def test_override_id():
    class StrIdClass(Base):
        id = sa.Column(sa.String, primary_key=True, doc="primary key")

    assert hasattr(StrIdClass, 'id')
    try:
        intId = StrIdClass(12)
        assert isinstance(intId, str)  # should not run... is this best?
    except:
        pass
