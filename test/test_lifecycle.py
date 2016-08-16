"""
Static data models don't have much to test, but this is a place to load
the various models and ensure the results are as expected.

Session setup and custom data types the only things that might go wrong.
"""
import datetime
import json
import os
import random
import string
import unittest

from jsonschema import validate
from ledger import Amount
from sqlalchemy_models import (sa, generate_signature_class, Base,
                               create_session_engine, setup_database, get_schemas, jsonify2,
                               user as um, wallet as wm, exchange as em)
from tapp_config import get_config

from sqlalchemy_models.util import create_user, build_definitions, multiply_tickers

SCHEMAS = get_schemas()


def test_create_session_engine_cfg():
    cfg = get_config("helper")
    ses, eng = create_session_engine(cfg=cfg)
    assert str(eng.url) == cfg.get('db', 'SA_ENGINE_URI')


# def test_create_session_engine_uri():
#     uri = "sqlite:////tmp/uri_test.db"
#     ses, eng = create_session_engine(uri=uri)
#     assert str(eng.url) == uri
#
#
#
#
# def test_setup_db_model():
#     uri = "/tmp/uri_test.db"
#     try:
#         os.remove(uri)
#     except OSError:
#         pass
#     uri = 'sqlite:///' + uri
#     ses, eng = create_session_engine(uri=uri)
#     setup_database(eng, models=[um.User])
#     ses.add(um.User(username='testuser'))
#     try:
#         ses.commit()
#     except Exception as e:
#         print e
#         assert e == "should not throw an error"


class TestSetupLogger(unittest.TestCase):
    def setUp(self):
        self.ses, self.eng = create_session_engine(cfg=get_config("helper"))
        setup_database(self.eng, modules=[um, em, wm])

    def tearDown(self):
        self.ses.close()
    #     try:
    #         os.remove(self.uri)
    #     except OSError:
    #         pass

    def test_User(self):
        address = ''.join([random.choice(string.ascii_letters) for n in xrange(19)])
        userdict = {'username': address[0:8]}
        user_key = {'key': address, 'keytype': 'public'}

        user = um.User(**userdict)
        self.ses.add(user)
        self.ses.commit()
        user_schema = SCHEMAS['User']
        udict = json.loads(jsonify2(user, 'User'))
        assert validate(udict, user_schema) is None

        user_key['user_id'] = user.id
        ukey = um.UserKey(**user_key)
        self.ses.add(ukey)
        self.ses.commit()
        ukey_schema = SCHEMAS['UserKey']
        ukey_dict = json.loads(jsonify2(ukey, 'UserKey'))
        del ukey_dict['user']
        assert validate(ukey_dict, ukey_schema) is None

    def test_create_user(self):
        address = ''.join([random.choice(string.ascii_letters) for n in xrange(19)])
        userdict = {'username': address[0:8]}
        user = create_user(userdict['username'], address, self.ses)
        assert user.username == userdict['username']
        ukey = self.ses.query(um.UserKey).filter(um.UserKey.user_id == user.id).first()
        assert ukey.key == address

    def test_override_id(self):
        class StrIdClass(Base):
            id = sa.Column(sa.String, primary_key=True, doc="primary key")

        assert hasattr(StrIdClass, 'id')
        try:
            intid = StrIdClass(12)
            assert isinstance(intid, str)  # should not run... is this best?
        except:
            pass

    def test_load_trade(self):
        tid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
        trade = em.Trade(tid, 'helper', 'BTC_USD', 'sell',
                         Amount("%s BTC" % 1.1), Amount("%s USD" % 770),
                         Amount("%s USD" % 1), 'quote', datetime.datetime.utcnow())
        print trade
        self.ses.add(trade)
        self.ses.commit()
        trade.load_commodities()
        dbtrade = self.ses.query(em.Trade).filter(em.Trade.trade_id == "helper|%s" % tid).one()
        assert dbtrade is not None
        assert isinstance(dbtrade.price, Amount)
        assert isinstance(dbtrade.amount, Amount)
        assert isinstance(dbtrade.fee, Amount)
        assert "770.00000000 USD" == str(dbtrade.price)
        assert "1.10000000 BTC" == str(dbtrade.amount)
        assert "1.00000000 USD" == str(dbtrade.fee)

    def test_load_ticker(self):
        ticker = em.Ticker(Amount("%s USD" % 769), Amount("%s USD" % 771),
                           Amount("%s USD" % 800), Amount("%s USD" % 700),
                           Amount("%s BTC" % 10000.1), Amount("%s USD" % 770),
                           'BTC_USD', 'helper')
        self.ses.add(ticker)
        self.ses.commit()
        ticker.load_commodities()
        dbtick = self.ses.query(em.Ticker).order_by(em.Ticker.time.desc()).first()
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

    def test_load_limit_order(self):
        oid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
        order = em.LimitOrder(Amount("{0:.8f} USD".format(770)), Amount("{0:.8f} BTC".format(1.1)),
                              'BTC_USD', 'ask', 'helper', oid)
        self.ses.add(order)
        self.ses.commit()
        order.load_commodities()
        dbo = self.ses.query(em.LimitOrder).order_by(em.LimitOrder.create_time.desc()).first()
        assert dbo is not None
        assert isinstance(dbo.price, Amount)
        assert isinstance(dbo.amount, Amount)
        assert "770.00000000 USD" == str(dbo.price)
        assert "1.10000000 BTC" == str(dbo.amount)

    # noinspection PyAugmentAssignment,PyAugmentAssignment
    def test_load_balance(self):
        uname = ''.join([random.choice(string.ascii_letters) for letter in xrange(9)])
        u = um.User(username=uname)
        self.ses.add(u)
        self.ses.commit()
        ref = ''.join([random.choice(string.ascii_letters) for letter in xrange(9)])
        bal = wm.Balance(Amount("{0:.8f} BTC".format(1.1)), Amount("{0:.8f} BTC".format(1.01)),
                         'BTC', ref, u.id)
        self.ses.add(bal)
        bal2 = wm.Balance(Amount("{0:.8f} USD".format(100)), Amount("{0:.8f} BTC".format(100)),
                          'USD', ref, u.id)
        self.ses.add(bal2)
        self.ses.commit()
        bal.load_commodities()
        bal2.load_commodities()
        bid = bal.id
        bid2 = bal2.id
        #self.ses.close()
        dbb = self.ses.query(wm.Balance).filter(wm.Balance.id == bid).first()
        assert dbb is not None
        assert isinstance(dbb.available, Amount)
        assert isinstance(dbb.total, Amount)
        assert "1.10000000 BTC" == str(dbb.total)
        assert "1.01000000 BTC" == str(dbb.available)

        amount = Amount("%s BTC" % 0.01)
        dbb.available = dbb.available + amount
        dbb.total = dbb.total + amount
        self.ses.add(dbb)
        self.ses.commit()
        dbb.load_commodities()
        dbb2 = self.ses.query(wm.Balance).filter(wm.Balance.id == bid2).first()
        dbb2.load_commodities()
        assert dbb2 is not None
        assert isinstance(dbb2.available, Amount)
        assert isinstance(dbb2.total, Amount)
        assert "100.00000000 USD" == str(dbb2.total)
        assert "100.00000000 USD" == str(dbb2.available)

    def test_credit_ledger(self):
        user = um.User(username=''.join([random.choice(string.ascii_letters) for letter in xrange(8)]))
        self.ses.add(user)
        self.ses.commit()
        tid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
        date = datetime.datetime.utcfromtimestamp(1468126581)
        credit = wm.Credit(Amount("%s BTC" % 1.1), tid, 'BTC', 'Bitcoin',
                           'complete', 'helper', 'helper|%s' % tid, user.id, date)

        le = credit.get_ledger_entry()
        ex = """2016/07/10 04:56:21 helper credit BTC
    Assets:helper:BTC:credit    1.10000000 BTC
    Equity:Wallet:BTC:debit   -1.10000000 BTC

"""
        assert le == ex

    def test_debit_ledger(self):
        user = um.User(username=''.join([random.choice(string.ascii_letters) for letter in xrange(8)]))
        self.ses.add(user)
        self.ses.commit()
        tid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
        date = datetime.datetime.utcfromtimestamp(1468126581)
        debit = wm.Debit(-Amount("%s BTC" % 1.1), Amount("%s BTC" % 0.0001), tid, 'BTC', 'Bitcoin',
                         'complete', 'helper', 'helper|%s' % tid, user.id, date)

        le = debit.get_ledger_entry()
        ex = """2016/07/10 04:56:21 helper debit BTC
    Assets:helper:BTC:debit    -1.10000000 BTC
    Equity:Wallet:BTC:credit   1.09990000 BTC
    Expenses:MinerFee   0.00010000 BTC

"""
        assert le == ex


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


def test_trade_ledger():
    tid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
    date = datetime.datetime.utcfromtimestamp(1468126581)
    trade = em.Trade(tid, 'helper', 'BTC_USD', 'sell',
                     Amount("%s BTC" % 1.1), Amount("%s USD" % 770),
                     Amount("%s USD" % 1), 'quote', date)
    le = trade.get_ledger_entry()
    ex = """P 2016/07/10 04:56:21 BTC 770.00000000 USD
P 2016/07/10 04:56:21 USD 0.00129870 BTC
2016/07/10 04:56:21 helper BTC_USD sell
    ;<Trade(trade_id='helper|{0}', side='sell', amount=1.10000000 BTC, price=770.00000000 USD, fee=1.00000000 USD, fee_side='quote', market='BTC_USD', exchange='helper', time=2016-07-10T04:56:21+00:00)>
    Assets:helper:USD    846.00000000 USD @ 0.00129870 BTC
    FX:BTC_USD:sell   -847.00000000 USD @ 0.00129870 BTC
    Assets:helper:BTC    -1.10000000 BTC @ 770.00000000 USD
    FX:BTC_USD:sell   1.10000000 BTC @ 770.00000000 USD
    Expenses:TradeFee    1.00000000 USD @ 0.00129870 BTC
""".format(tid)
    assert le == ex

    tid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
    trade = em.Trade(tid, 'helper', 'BTC_USD', 'buy',
                     Amount("%s BTC" % 1.1), Amount("%s USD" % 770),
                     Amount("%s USD" % 1), 'quote', date)
    le = trade.get_ledger_entry()
    ex = """P 2016/07/10 04:56:21 BTC 770.00000000 USD
P 2016/07/10 04:56:21 USD 0.00129870 BTC
2016/07/10 04:56:21 helper BTC_USD buy
    ;<Trade(trade_id='helper|{0}', side='buy', amount=1.10000000 BTC, price=770.00000000 USD, fee=1.00000000 USD, fee_side='quote', market='BTC_USD', exchange='helper', time=2016-07-10T04:56:21+00:00)>
    Assets:helper:USD    -848.00000000 USD @ 0.00129870 BTC
    FX:BTC_USD:buy   847.00000000 USD @ 0.00129870 BTC
    Assets:helper:BTC    1.10000000 BTC @ 770.00000000 USD
    FX:BTC_USD:buy   -1.10000000 BTC @ 770.00000000 USD
    Expenses:TradeFee    1.00000000 USD @ 0.00129870 BTC
""".format(tid)
    assert le == ex

    tid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
    trade = em.Trade(tid, 'helper', 'BTC_USD', 'sell',
                     Amount("%s BTC" % 1.1), Amount("%s USD" % 770),
                     Amount("%s BTC" % 0.01), 'base', date)
    le = trade.get_ledger_entry()
    ex = """P 2016/07/10 04:56:21 BTC 770.00000000 USD
P 2016/07/10 04:56:21 USD 0.00129870 BTC
2016/07/10 04:56:21 helper BTC_USD sell
    ;<Trade(trade_id='helper|{0}', side='sell', amount=1.10000000 BTC, price=770.00000000 USD, fee=0.01000000 BTC, fee_side='base', market='BTC_USD', exchange='helper', time=2016-07-10T04:56:21+00:00)>
    Assets:helper:USD    839.30000000 USD @ 0.00129870 BTC
    FX:BTC_USD:sell   -839.30000000 USD @ 0.00129870 BTC
    Assets:helper:BTC    -1.10000000 BTC @ 770.00000000 USD
    FX:BTC_USD:sell   1.09000000 BTC @ 770.00000000 USD
    Expenses:TradeFee    0.01000000 BTC @ 770.00000000 USD
""".format(tid)
    assert le == ex

    tid = ''.join([random.choice(string.ascii_letters) for letter in xrange(19)])
    trade = em.Trade(tid, 'helper', 'BTC_USD', 'buy',
                     Amount("%s BTC" % 1.1), Amount("%s USD" % 770),
                     Amount("%s BTC" % 0.01), 'base', date)
    le = trade.get_ledger_entry()
    ex = """P 2016/07/10 04:56:21 BTC 770.00000000 USD
P 2016/07/10 04:56:21 USD 0.00129870 BTC
2016/07/10 04:56:21 helper BTC_USD buy
    ;<Trade(trade_id='helper|{0}', side='buy', amount=1.10000000 BTC, price=770.00000000 USD, fee=0.01000000 BTC, fee_side='base', market='BTC_USD', exchange='helper', time=2016-07-10T04:56:21+00:00)>
    Assets:helper:USD    -847.00000000 USD @ 0.00129870 BTC
    FX:BTC_USD:buy   847.00000000 USD @ 0.00129870 BTC
    Assets:helper:BTC    1.09000000 BTC @ 770.00000000 USD
    FX:BTC_USD:buy   -1.10000000 BTC @ 770.00000000 USD
    Expenses:TradeFee    0.01000000 BTC @ 770.00000000 USD
""".format(tid)
    assert le == ex


def test_build_definitions():
    try:
        os.remove("sqlalchemy_models/_definitions.json")
    except OSError:
        pass
    build_definitions()
    assert os.path.exists("sqlalchemy_models/_definitions.json")
    assert os.path.exists("sqlalchemy_models/definitions.json")


def test_ticker_encoding():
    ticker = em.Ticker(769, 771, 800, 700, 10000.1, 770, 'BTC_USD', 'helper')
    jticker = jsonify2(ticker, 'Ticker')
    ticker.load_commodities()
    dticker = json.loads(jticker)
    from_jticker = em.Ticker.from_json(jticker)
    assert ticker.bid == from_jticker.bid
    assert ticker.ask == from_jticker.ask
    assert ticker.high == from_jticker.high
    assert ticker.low == from_jticker.low
    assert ticker.volume == from_jticker.volume
    assert ticker.time == from_jticker.time
    from_dticker = em.Ticker.from_dict(dticker)
    assert ticker.bid == from_dticker.bid
    assert ticker.ask == from_dticker.ask
    assert ticker.high == from_dticker.high
    assert ticker.low == from_dticker.low
    assert ticker.volume == from_dticker.volume
    assert ticker.time == from_dticker.time


def test_ticker_multiply():
    usdticker = em.Ticker(769, 771, 800, 700, 10000.1, 770, 'BTC_USD', 'helper')
    usdticker.load_commodities()
    dashticker = em.Ticker(0.0199, 0.0201, 0.021, 0.02, 1000000.1, 0.02, 'DASH_BTC', 'helper')
    dashticker.load_commodities()
    dashusdticker = multiply_tickers(dashticker, usdticker)
    assert dashusdticker.market == 'DASH_USD'
    assert dashusdticker.bid == Amount("%s USD" % 15.3031)
    assert dashusdticker.ask == Amount("%s USD" % 15.4971)
    assert dashusdticker.high == Amount("%s USD" % 16.8)
    assert dashusdticker.last == Amount("%s USD" % 15.4)


def test_ticker_index():
    ticker = em.Ticker(769, 773, 800, 700, 10000.1, 771, 'BTC_USD', 'helper')
    ticker.load_commodities()
    index = ticker.calculate_index()
    assert index == Amount("{0:.8f} USD".format(771))
