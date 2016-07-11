"""
SQLAlchemy models for Wallets
"""
from . import sa, orm, Base, LedgerAmount
from ledger import Amount
import datetime

__all__ = ['LimitOrder', 'Ticker', 'Trade']


class LimitOrder(Base):
    time = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    price = sa.Column(LedgerAmount, nullable=False)
    amount = sa.Column(LedgerAmount, nullable=False)
    market = sa.Column(sa.String(9), nullable=False)
    side = sa.Column(sa.Enum("bid", "ask"), nullable=False)
    exchange = sa.Column(sa.String(12), nullable=False)
    order_id = sa.Column(sa.String(80), unique=True, nullable=False)

    def __init__(self, price, amount, market, side, exchange, order_id):
        self.price = price
        self.amount = amount
        self.market = market
        self.side = side
        self.exchange = exchange
        self.order_id = "%s|%s" % (exchange, order_id)  # to ensure uniqueness

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


class Ticker(Base):
    time = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    bid = sa.Column(LedgerAmount, nullable=False)
    ask = sa.Column(LedgerAmount, nullable=False)
    high = sa.Column(LedgerAmount, nullable=False)
    low = sa.Column(LedgerAmount, nullable=False)
    volume = sa.Column(LedgerAmount, nullable=False)
    last = sa.Column(LedgerAmount, nullable=False)
    market = sa.Column(sa.String(9), nullable=False)
    exchange = sa.Column(sa.String(12), nullable=False)

    def __init__(self, bid, ask, high, low, volume, last, market, exchange):
        self.bid = bid
        self.ask = ask
        self.high = high
        self.low = low
        self.volume = volume
        self.last = last
        self.market = market
        self.exchange = exchange

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
    trade_id = sa.Column(sa.String(80), unique=True, nullable=False)
    exchange = sa.Column(sa.String(12), nullable=False)
    market = sa.Column(sa.String(9), nullable=False)
    side = sa.Column(sa.Enum("buy", "sell"), nullable=False)
    amount = sa.Column(LedgerAmount, nullable=False)
    price = sa.Column(LedgerAmount, nullable=False)
    fee = sa.Column(LedgerAmount, nullable=False)
    fee_side = sa.Column(sa.String(4), nullable=False)
    time = sa.Column(sa.DateTime(), nullable=False)

    def __init__(self, trade_id, exchange, market, side, amount, price, fee,
                 fee_side, time):
        self.trade_id = "%s|%s" % (exchange, trade_id)  # to ensure uniqueness
        self.exchange = exchange
        self.market = market
        self.side = side
        self.amount = amount
        self.price = price
        self.fee = fee
        self.fee_side = fee_side
        self.time = time

    def __repr__(self):
        return "<Trade(trade_id='%s', side='%s', amount=%s, price=%s, fee=%s, fee_side='%s', market='%s', exchange='%s', time=%s)>" % (
            self.trade_id, self.side, self.amount,
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
        ledger += "%s %s %s %s\n" % (date, self.exchange, self.market, self.side)
        ledger += "    ;%s\n" % repr(self)

        feeline = "\n"
        if self.fee > 0:
            feeline = "    Expenses:TradeFee    {0} @ ".format(self.fee)
            if self.fee_side == 'base':
                feeline += "{0}\n".format(self.price)
                if self.side == 'sell':
                    b_vol = self.amount - self.fee
                    b_mine = -self.amount
                    q_vol = -Amount(
                        "{{0:.{0}}} {1}".format(self.price.precision, quote).format(self.price * b_vol.number()))
                    # setattr(q_vol, 'precision', self.price.precision)
                    q_mine = -q_vol
                else:
                    b_vol = -self.amount
                    b_mine = self.amount - self.fee

                    q_vol = Amount(
                        "{{0:.{0}}} {1}".format(self.price.precision, quote).format(self.price * self.amount.number()))
                    # setattr(q_vol, 'precision', self.price.precision)
                    q_mine = -q_vol
            else:
                feeline += "{0}\n".format(q_price)
                if self.side == 'sell':
                    b_vol = self.amount
                    b_mine = -self.amount
                    q_vol = -Amount(
                        "{{0:.{0}}} {1}".format(self.price.precision, quote).format(self.price * self.amount.number()))
                    # setattr(q_vol, 'precision', self.price.precision)
                    q_mine = -q_vol - self.fee
                else:
                    b_vol = -self.amount
                    b_mine = self.amount
                    q_vol = Amount(
                        "{{0:.{0}}} {1}".format(self.price.precision, quote).format(self.price * self.amount.number()))
                    # setattr(q_vol, 'precision', self.price.precision)
                    q_mine = -q_vol - self.fee
        else:
            if self.side == 'sell':
                b_vol = self.amount
                b_mine = -self.amount
                q_vol = -self.price * self.amount.number()
                # setattr(q_vol, 'precision', self.price.precision)
                q_mine = -q_vol
            else:
                b_vol = -self.amount
                b_mine = self.amount
                q_vol = self.price * self.amount.number()
                # setattr(q_vol, 'precision', self.price.precision)
                q_mine = -q_vol

        ledger += "    Assets:{0}:{1}    {2} @ {3}\n".format(self.exchange, quote, q_mine, q_price)
        ledger += "    FX:{0}:{1}   {2} @ {3}\n".format(self.market, self.side, q_vol, q_price)
        ledger += "    Assets:{0}:{1}    {2} @ {3}\n".format(self.exchange, base, b_mine, self.price)
        ledger += "    FX:{0}:{1}   {2} @ {3}\n".format(self.market, self.side, b_vol, self.price)
        ledger += feeline
        return ledger
