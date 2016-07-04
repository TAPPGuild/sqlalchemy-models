"""
Static data models don't have much to test, but this is a place to load
the various models and ensure the results are as expected.

Lazy loading and custom data types the only things that might go wrong.
"""
import alchemyjsonschema as ajs
import copy
import datetime
import json
import pytest
import random
import string
import time
from alchemyjsonschema.dictify import jsonify
from jsonschema import validate
from ledger import Amount
from sqlalchemy_models import (sa, orm, generate_signature_class, Base,
                               LedgerAmount, create_session_engine, 
                               setup_database,
                               user as um, wallet as wm, exchange as em)

eng_URI = 'sqlite:////tmp/test.db'
ses, eng = create_session_engine(uri=eng_URI)

ADDRESS = ''.join([random.choice(string.ascii_letters) for n in xrange(19)])
USER = {'username': ADDRESS[0:8]}
USER_KEY = {'key': ADDRESS, 'keytype': 'public'}

setup_database(eng, modules=[um, wm, em])

factory = ajs.SchemaFactory(ajs.AlsoChildrenWalker)


def test_User():
    user = um.User(**USER)
    ses.add(user)
    ses.commit()
    user_schema = factory.__call__(um.User)
    #print user_schema
    #print json.dumps(user_schema, indent=4)
    udict = jsonify(user, user_schema)
    assert validate(udict, user_schema) is None

    USER_KEY['user_id'] = user.id
    ukey = um.UserKey(**USER_KEY)
    ses.add(ukey)
    ses.commit()
    ukey_schema = factory.__call__(um.UserKey)
    ukey_dict = jsonify(ukey, ukey_schema)
    #print ukey_schema
    del ukey_dict['user']
    #print json.dumps(ukey_schema, indent=4)
    assert validate(ukey_dict, ukey_schema) is None


def test_names():
    assert um.User.__name__ == 'User'
    assert um.User.__tablename__ == 'user'
    assert um.UserKey.__name__ == 'UserKey'
    assert um.UserKey.__tablename__ == 'user_key'


def test_signature_class():
    sigclass = generate_signature_class(um.User)
    assert hasattr(sigclass, 'data')
    assert hasattr(sigclass, 'id')
    assert hasattr(sigclass, '%s_id' % 'user')
    assert sigclass.__name__ == 'UserSigs'
    assert sigclass.__tablename__ == 'user_sigs'
    sigkeyclass = generate_signature_class(um.UserKey)
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


def test_load_trade():
    tid = ''.join([random.choice(string.ascii_letters) for n in xrange(19)])
    trade = em.Trade(tid, 'testx', 'BTC_USD', 'sell',
                     Amount("%s BTC" % 1.1), Amount("%s USD" % 770),
                     Amount("%s USD" % 1), 'quote', datetime.datetime.utcnow())
    ses.add(trade)
    ses.commit()
    ses.close()
    dbtrade = ses.query(em.Trade).filter(em.Trade.trade_id=="testx|%s" % tid).one()
   # dbtrade.load_trade_commodities()
    print dbtrade
    assert dbtrade is not None
    assert isinstance(dbtrade.price, Amount)
    assert isinstance(dbtrade.amount, Amount)
    assert isinstance(dbtrade.fee, Amount)
    assert "770.00000000 USD" == str(dbtrade.price)
    assert "1.10000000 BTC" == str(dbtrade.amount)
    assert "1.00000000 USD" == str(dbtrade.fee)


def test_load_ticker():
    ticker = em.Ticker(Amount("%s USD" % 769), Amount("%s USD" % 771), 
                      Amount("%s USD" % 800), Amount("%s USD" % 700),
                      Amount("%s BTC" % 10000.1), Amount("%s USD" % 770),
                      'BTC_USD', 'testx')
    ses.add(ticker)
    ses.commit()
    ses.close()
    dbtick = ses.query(em.Ticker).order_by(em.Ticker.time.desc()).first()
    ses.close()
    print dbtick
    assert dbtick is not None
    assert isinstance(dbtick.bid, Amount)
    assert isinstance(dbtick.ask, Amount)
    assert isinstance(dbtick.high, Amount)
    assert isinstance(dbtick.low, Amount)
    assert isinstance(dbtick.volume, Amount)
    assert isinstance(dbtick.last, Amount)
    assert "770.00000000 USD" == str(dbtick.last)
    assert "10000.10000000 BTC" == str(dbtick.volume)
    assert "769.00000000 USD" == str(dbtick.bid)


def test_load_limit_order():
    oid = ''.join([random.choice(string.ascii_letters) for n in xrange(19)])
    order = em.LimitOrder(Amount("%s USD" % 770), Amount("%s BTC" % 1.1), 
                          'BTC_USD', 'ask', 'testx', oid)
    ses.add(order)
    ses.commit()
    ses.close()
    dbo = ses.query(em.LimitOrder).order_by(em.LimitOrder.time.desc()).first()
    print dbo
    assert dbo is not None
    assert isinstance(dbo.price, Amount)
    assert isinstance(dbo.amount, Amount)
    assert "770.00000000 USD" == str(dbo.price)
    assert "1.10000000 BTC" == str(dbo.amount)


def test_load_balance():
    uname = ''.join([random.choice(string.ascii_letters) for n in xrange(9)])
    u = um.User(username=uname)
    ses.add(u)
    ses.commit()
    ref = ''.join([random.choice(string.ascii_letters) for n in xrange(9)])
    bal = wm.Balance(Amount("%s BTC" % 1.1), Amount("%s BTC" % 1.01), 
                          'BTC', ref, u.id)
    ses.add(bal)
    bal2 = wm.Balance(Amount("%s USD" % 100), Amount("%s BTC" % 100), 
                            'USD', ref, u.id)
    ses.add(bal2)

    ses.commit()
    bid = bal.id
    bid2 = bal2.id
    ses.close()
    dbb = ses.query(wm.Balance).filter(wm.Balance.id == bid).first()
    assert dbb is not None
    assert isinstance(dbb.available, Amount)
    assert isinstance(dbb.total, Amount)
    assert "1.10000000 BTC" == str(dbb.total)
    assert "1.01000000 BTC" == str(dbb.available)

    amount = Amount("%s BTC" % 0.01)
    dbb.available = dbb.available + amount
    dbb.total = dbb.total + amount
    ses.add(dbb)
    ses.commit()

    dbb2 = ses.query(wm.Balance).filter(wm.Balance.id == bid2).first()
    assert dbb2 is not None
    assert isinstance(dbb2.available, Amount)
    assert isinstance(dbb2.total, Amount)
    assert "100.00000000 USD" == str(dbb2.total)
    assert "100.00000000 USD" == str(dbb2.available)

