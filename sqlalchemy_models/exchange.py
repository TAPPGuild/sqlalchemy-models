"""
SQLAlchemy models for Exchanges
"""
import random
import string

from __init__ import sa, orm, Base, LedgerAmount
from ledger import Amount
import datetime

__all__ = ['LimitOrder', 'Ticker', 'Trade']


class LimitOrder(Base):
    id = sa.Column(sa.Integer, sa.Sequence('limit_order_id_seq'), primary_key=True)
    create_time = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    change_time = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    price = sa.Column(LedgerAmount, nullable=False)
    amount = sa.Column(LedgerAmount, nullable=False)
    exec_amount = sa.Column(LedgerAmount, nullable=False)
    market = sa.Column(sa.String(9), nullable=False)
    side = sa.Column(sa.Enum("bid", "ask", name='order_side'), nullable=False)
    exchange = sa.Column(sa.String(12), nullable=False)
    order_id = sa.Column(sa.String(80), unique=True, nullable=False)
    state = sa.Column(sa.Enum('pending', 'open', 'closed', name='state'))

    def __init__(self, price, amount, market, side, exchange, order_id=None, create_time=datetime.datetime.utcnow(),
                 change_time=datetime.datetime.utcnow(), exec_amount=0, state='pending'):
        self.price = price
        self.amount = amount
        self.market = market
        self.side = side
        self.exchange = exchange
        if order_id is None:
            self.order_id = "tmp|%s" % ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
        elif "|" not in str(order_id):
            self.order_id = "%s|%s" % (exchange, order_id)  # to ensure uniqueness
        else:
            self.order_id = order_id
        self.create_time = create_time
        self.change_time = change_time
        self.exec_amount = exec_amount
        self.state = state
        self.load_commodities()

    def __repr__(self):
        return "<LimitOrder(price=%s, amount=%s, exec_amount=%s, market='%s', side='%s', exchange='%s', order_id='%s', " \
               "state='%s', create_time=%s)>" % (
                    self.price, self.amount, self.exec_amount,
                    self.market, self.side, self.exchange,
                    self.order_id, self.state, self.create_time.strftime('%Y/%m/%d %H:%M:%S'))

    @orm.reconstructor
    def load_commodities(self):
        """
        Load the commodities for Amounts in this object.
        """
        base, quote = self.market.split("_")
        if isinstance(self.price, Amount):
            self.price = Amount("{0:.8f} {1}".format(self.price.to_double(), quote))
        else:
            self.price = Amount("{0:.8f} {1}".format(self.price, quote))
        if isinstance(self.amount, Amount):
            self.amount = Amount("{0:.8f} {1}".format(self.amount.to_double(), base))
        else:
            self.amount = Amount("{0:.8f} {1}".format(self.amount, base))
        if isinstance(self.exec_amount, Amount):
            self.exec_amount = Amount("{0:.8f} {1}".format(self.exec_amount.to_double(), base))
        else:
            self.exec_amount = Amount("{0:.8f} {1}".format(self.exec_amount, base))


class Ticker(Base):
    id = sa.Column(sa.Integer, sa.Sequence('ticker_id_seq'),  primary_key=True)
    time = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    bid = sa.Column(LedgerAmount, nullable=False)
    ask = sa.Column(LedgerAmount, nullable=False)
    high = sa.Column(LedgerAmount, nullable=False)
    low = sa.Column(LedgerAmount, nullable=False)
    volume = sa.Column(LedgerAmount, nullable=False)
    last = sa.Column(LedgerAmount, nullable=False)
    market = sa.Column(sa.String(9), nullable=False)
    exchange = sa.Column(sa.String(12), nullable=False)

    def __init__(self, bid, ask, high, low, volume, last, market, exchange, time=None):
        self.bid = bid
        self.ask = ask
        self.high = high
        self.low = low
        self.volume = volume
        self.last = last
        self.market = market
        self.exchange = exchange
        self.time = time if time is not None else datetime.datetime.utcnow()
        self.load_commodities()

    def __repr__(self):
        return "<Ticker(bid=%s, ask=%s, high=%s, low=%s, volume=%s, last=%s, market='%s', exchange='%s', time=%s)>" % (
            self.bid, self.ask, self.high,
            self.low, self.volume, self.last,
            self.market, self.exchange, self.time.strftime('%Y/%m/%d %H:%M:%S'))

    @orm.reconstructor
    def load_commodities(self):
        """
        Load the commodities for Amounts in this object.
        """
        base, quote = self.market.split("_")
        if isinstance(self.bid, Amount):
            self.bid = Amount("{0:.8f} {1}".format(self.bid.to_double(), quote))
        else:
            self.bid = Amount("{0:.8f} {1}".format(self.bid, quote))
        if isinstance(self.ask, Amount):
            self.ask = Amount("{0:.8f} {1}".format(self.ask.to_double(), quote))
        else:
            self.ask = Amount("{0:.8f} {1}".format(self.ask, quote))
        if isinstance(self.high, Amount):
            self.high = Amount("{0:.8f} {1}".format(self.high.to_double(), quote))
        else:
            self.high = Amount("{0:.8f} {1}".format(self.high, quote))
        if isinstance(self.low, Amount):
            self.low = Amount("{0:.8f} {1}".format(self.low.to_double(), quote))
        else:
            self.low = Amount("{0:.8f} {1}".format(self.low, quote))
        if isinstance(self.volume, Amount):
            self.volume = Amount("{0:.8f} {1}".format(self.volume.to_double(), base))
        else:
            self.volume = Amount("{0:.8f} {1}".format(self.volume, base))
        if isinstance(self.last, Amount):
            self.last = Amount("{0:.8f} {1}".format(self.last.to_double(), quote))
        else:
            self.last = Amount("{0:.8f} {1}".format(self.last, quote))


class Trade(Base):
    id = sa.Column(sa.Integer, sa.Sequence('trade_id_seq'), primary_key=True)
    trade_id = sa.Column(sa.String(80), unique=True, nullable=False)
    exchange = sa.Column(sa.String(12), nullable=False)
    market = sa.Column(sa.String(9), nullable=False)
    trade_side = sa.Column(sa.Enum('buy', 'sell', name='trade_side'), nullable=False)
    amount = sa.Column(LedgerAmount, nullable=False)
    price = sa.Column(LedgerAmount, nullable=False)
    fee = sa.Column(LedgerAmount, nullable=False)
    fee_side = sa.Column(sa.String(5), nullable=False)
    time = sa.Column(sa.DateTime(), nullable=False)

    def __init__(self, trade_id, exchange, market, side, amount, price, fee,
                 fee_side, time=None):
        self.trade_id = "%s|%s" % (exchange, trade_id)  # to ensure uniqueness
        self.exchange = exchange
        self.market = market
        self.trade_side = side
        self.amount = amount
        self.price = price
        self.fee = fee
        self.fee_side = fee_side
        self.time = time if time is not None else datetime.datetime.utcnow()
        self.load_commodities()

    # noinspection PyPep8
    def __repr__(self):
        return "<Trade(trade_id='%s', side='%s', amount=%s, price=%s, fee=%s, fee_side='%s', market='%s', " \
               "exchange='%s', time=%s)>" % (
                   self.trade_id, self.trade_side, self.amount,
                   self.price, self.fee, self.fee_side,
                   self.market, self.exchange, self.time.strftime('%Y/%m/%d %H:%M:%S'))

    @orm.reconstructor
    def load_commodities(self):
        """
        Load the commodities for Amounts in this object.
        """
        base, quote = self.market.split("_")
        if isinstance(self.price, Amount):
            self.price = Amount("{0:.8f} {1}".format(self.price.to_double(), quote))
        else:
            self.price = Amount("{0:.8f} {1}".format(float(self.price), quote))
        if isinstance(self.amount, Amount):
            self.amount = Amount("{0:.8f} {1}".format(self.amount.to_double(), base))
        else:
            self.amount = Amount("{0:.8f} {1}".format(float(self.amount), base))
        fee_currency = base if self.fee_side == 'base' else quote
        if isinstance(self.fee, Amount):
            self.fee = Amount("{0:.8f} {1}".format(float(self.fee.to_double()), fee_currency))
        else:
            self.fee = Amount("{0:.8f} {1}".format(float(self.fee), fee_currency))

    def get_ledger_entry(self):
        ledger = ""
        base, quote = self.market.split("_")
        date = self.time.strftime('%Y/%m/%d %H:%M:%S')

        ledger += "P %s %s %s\n" % (date, base, self.price)
        q_price = Amount("%s %s" % (self.price.quantity_string(), base)).inverted()
        ledger += "P %s %s %s\n" % (date, quote, q_price)
        ledger += "%s %s %s %s\n" % (date, self.exchange, self.market, self.trade_side)
        ledger += "    ;%s\n" % repr(self)

        feeline = "\n"
        if self.fee > 0:
            feeline = "    Expenses:TradeFee    {0} @ ".format(self.fee)
            if self.fee_side == 'base':
                feeline += "{0}\n".format(self.price)
                if self.trade_side == 'sell':
                    b_vol = self.amount - self.fee
                    b_mine = -self.amount
                    q_vol = -Amount(
                        "{0:.8} {1}".format(self.price * b_vol.number(), quote))
                    q_mine = -q_vol
                else:
                    b_vol = -self.amount
                    b_mine = self.amount - self.fee

                    q_vol = Amount(
                        "{0:.8} {1}".format(self.price * self.amount.number(), quote))
                    q_mine = -q_vol
            else:
                feeline += "{0}\n".format(q_price)
                if self.trade_side == 'sell':
                    b_vol = self.amount
                    b_mine = -self.amount
                    print "{0:.8} {1}".format(self.price * self.amount.number(), quote)
                    q_vol = -Amount(
                        "{0:.8} {1}".format(self.price * self.amount.number(), quote))
                    q_mine = -q_vol - self.fee
                else:
                    b_vol = -self.amount
                    b_mine = self.amount
                    q_vol = Amount(
                        "{0:.8} {1}".format(self.price * self.amount.number(), quote))
                    q_mine = -q_vol - self.fee
        else:
            if self.trade_side == 'sell':
                b_vol = self.amount
                b_mine = -self.amount
                q_vol = -self.price * self.amount.number()
                q_mine = -q_vol
            else:
                b_vol = -self.amount
                b_mine = self.amount
                q_vol = self.price * self.amount.number()
                q_mine = -q_vol

        ledger += "    Assets:{0}:{1}    {2} @ {3}\n".format(self.exchange, quote, q_mine, q_price)
        ledger += "    FX:{0}:{1}   {2} @ {3}\n".format(self.market, self.trade_side, q_vol, q_price)
        ledger += "    Assets:{0}:{1}    {2} @ {3}\n".format(self.exchange, base, b_mine, self.price)
        ledger += "    FX:{0}:{1}   {2} @ {3}\n".format(self.market, self.trade_side, b_vol, self.price)
        ledger += feeline
        return ledger
