"""
SQLAlchemy models for Wallets
"""
from . import sa, orm, Base, LedgerAmount
from ledger import Amount
import datetime


__all__ = ['Balance', 'Address', 'Credit', 'Debit', 'HWBalance']


class Balance(Base):
    """A user's balance in a single currency. Only the latest record is valid."""
    total = sa.Column(LedgerAmount, nullable=False)
    available = sa.Column(LedgerAmount, nullable=False)
    currency = sa.Column(sa.String(4), nullable=False)  # i.e. BTC, DASH, USD
    time = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    reference = sa.Column(sa.String(256), nullable=True)

    # foreign key reference to the owner of this
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False)
    user = orm.relationship("User", foreign_keys=[user_id])

    def __init__(self, total, available, currency, reference, user_id):
        self.total = total
        self.available = available
        self.currency = currency
        self.reference = reference
        self.user_id = user_id

    @orm.reconstructor
    def load_commodities(self):
        """
        Load the commodities for Amounts in this object.
        """
        if isinstance(self.available, Amount):
            self.available = Amount("{0:.8f} {1}".format(self.available.to_double(), self.currency))
        else:
            self.available = Amount("{0:.8f} {1}".format(self.available, self.currency))
        if isinstance(self.total, Amount):
            self.total = Amount("{0:.8f} {1}".format(self.total.to_double(), self.currency))
        else:
            self.total = Amount("{0:.8f} {1}".format(self.total, self.currency))


class Address(Base):
    """A payment network Address or account number."""
    address = sa.Column(sa.String(64), nullable=False)  # i.e. 1PkzTWAyfR9yoFw2jptKQ3g6E5nKXPsy8r, 	XhwWxABXPVG5Z3ePyLVA3VixPRkARK6FKy
    currency = sa.Column(sa.String(4), nullable=False)  # i.e. BTC, DASH, USD
    network = sa.Column(sa.String(64), nullable=False)  # i.e. Bitcoin, Dash, Crypto Capital
    state = sa.Column(sa.Enum("pending", "active", "blocked"), nullable=False)

    # foreign key reference to the owner of this
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False)
    user = orm.relationship("User", foreign_keys=[user_id])

    def __init__(self, address, currency, network, state, user_id):
        self.address = address
        self.currency = currency
        self.network = network
        self.state = state
        self.user_id = user_id


class Credit(Base):
    """A Credit, which adds tokens to a User's Balance."""
    amount = sa.Column(LedgerAmount, nullable=False)
    address = sa.Column(sa.String(64), nullable=False)  # i.e. 1PkzTWAyfR9yoFw2jptKQ3g6E5nKXPsy8r, XhwWxABXPVG5Z3ePyLVA3VixPRkARK6FKy
    currency = sa.Column(sa.String(4), nullable=False)  # i.e. BTC, DASH, USD
    network = sa.Column(sa.String(64), nullable=False)  # i.e. Bitcoin, Dash, Crypto Capital
    state = sa.Column(sa.Enum("unconfirmed", "complete", "error"), nullable=False)
    reference = sa.Column(sa.String(256), nullable=True)  # i.e. invoice#1
    ref_id = sa.Column(sa.String(256), nullable=False, unique=True)  # i.e. 4cef42f9ff334b9b11bffbd9da21da54176103d92c1c6e4442cbe28ca43540fd:0
    time = sa.Column(sa.DateTime(), nullable=False)

    # foreign key reference to the owner of this
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False)
    user = orm.relationship("User", foreign_keys=[user_id])

    def __init__(self, amount, address, currency, network, state, reference, ref_id, user_id, time):
        self.amount = amount
        self.address = address
        self.currency = currency
        self.network = network
        self.state = state
        self.reference = reference
        self.ref_id = ref_id
        self.user_id = user_id
        self.time = time

    def __repr__(self):
        return "<Credit(amount=%s, address='%s', currency='%s', network='%s', state='%s', reference='%s', ref_id='%s', time=%s)>" % (\
                    self.amount, self.address, self.currency, self.network,
                    self.state, self.reference, self.ref_id, self.time.strftime('%Y/%m/%d %H:%M:%S'))

    def get_ledger_entry(self):
        date = self.time.strftime('%Y/%m/%d %H:%M:%S')
        ledger = "%s %s %s %s\n" % (date, self.reference, 'credit', self.currency)
        ledger += "    Assets:{0}:{1}:credit    {2}\n".format(self.reference, self.currency, self.amount)
        ledger += "    Equity:Wallet:{0}:debit   {1}\n".format(self.currency, -self.amount)
        ledger += "\n"
        return ledger


    @orm.reconstructor
    def load_commodities(self):
        """
        Load the commodities for Amounts in this object.
        """
        if isinstance(self.amount, Amount):
            self.amount = Amount("{0:.8f} {1}".format(self.amount.to_double(), self.currency))
        else:
            self.amount = Amount("{0:.8f} {1}".format(self.amount, self.currency))


class Debit(Base):
    """A Debit, which subtracts tokens from a User's Balance."""
    amount = sa.Column(LedgerAmount, nullable=False)
    fee = sa.Column(LedgerAmount, nullable=False)
    address = sa.Column(sa.String(64), nullable=False)  # i.e. 1PkzTWAyfR9yoFw2jptKQ3g6E5nKXPsy8r,  XhwWxABXPVG5Z3ePyLVA3VixPRkARK6FKy
    currency = sa.Column(sa.String(4), nullable=False)  # i.e. BTC, DASH, USDT
    network = sa.Column(sa.String(64), nullable=False)  # i.e. Bitcoin, Dash, Crypto Capital
    state = sa.Column(sa.Enum("unconfirmed", "complete", "error"), nullable=False)
    reference = sa.Column(sa.String(256), nullable=True)  # i.e. invoice#1
    ref_id = sa.Column(sa.String(256), nullable=False)  # i.e. 4cef42f9ff334b9b11bffbd9da21da54176103d92c1c6e4442cbe28ca43540fd
    time = sa.Column(sa.DateTime(), nullable=False)

    # foreign key reference to the owner of this
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False)
    user = orm.relationship("User", foreign_keys=[user_id])

    def __init__(self, amount, fee, address, currency, network, state, reference, ref_id, user_id, time):
        self.amount = abs(amount)
        self.fee = abs(fee)
        self.address = address
        self.currency = currency
        self.network = network
        self.state = state
        self.reference = reference
        self.ref_id = ref_id
        self.user_id = user_id
        self.time = time

    def __repr__(self):
        return "<Debit(amount=%s, fee=%s, address='%s', currency='%s', network='%s', state='%s', reference='%s', ref_id='%s', time=%s)>" % (\
                    self.amount, self.fee, self.address,
                    self.currency, self.network, self.state,
                    self.reference, self.ref_id, self.time.strftime('%Y/%m/%d %H:%M:%S'))

    def get_ledger_entry(self):
        date = self.time.strftime('%Y/%m/%d %H:%M:%S')
        ledger = "%s %s %s %s\n" % (date, self.reference, 'debit', self.currency)
        assert self.amount > 0
        ledger += "    Assets:{0}:{1}:debit    {2}\n".format(self.reference, self.currency, -self.amount)
        if self.fee > 0:
            ledger += "    Equity:Wallet:{0}:credit   {1}\n".format(self.currency, self.amount - self.fee)
            ledger += "    Expenses:MinerFee   {0}\n".format(self.fee)
        else:
            ledger += "    Equity:Wallet:{0}:credit   {1}\n".format(self.currency, self.amount)
        ledger += "\n"
        return ledger

    @orm.reconstructor
    def load_commodities(self):
        """
        Load the commodities for Amounts in this object.
        """
        if isinstance(self.fee, Amount):
            self.fee = Amount("{0:.8f} {1}".format(self.fee.to_double(), self.currency))
        else:
            self.fee = Amount("{0:.8f} {1}".format(self.fee, self.currency))
        if isinstance(self.amount, Amount):
            self.amount = Amount("{0:.8f} {1}".format(self.amount.to_double(), self.currency))
        else:
            self.amount = Amount("{0:.8f} {1}".format(self.amount, self.currency))


class HWBalance(Base):
    """A Hot Wallet Balance, for internal use only"""
    available = sa.Column(LedgerAmount, nullable=False)
    total = sa.Column(LedgerAmount, nullable=False)
    currency = sa.Column(sa.String(4), nullable=False)  # i.e. BTC, DASH, USDT
    network = sa.Column(sa.String(64), nullable=False)  # i.e. Bitcoin, Dash, Crypto Capital
    time = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, available, total, currency, network):
        self.available = available
        self.total = total
        self.currency = currency
        self.network = network

    @orm.reconstructor
    def load_commodities(self):
        """
        Load the commodities for Amounts in this object.
        """
        if isinstance(self.available, Amount):
            self.available = Amount("{0:.8f} {1}".format(self.available.to_double(), self.currency))
        else:
            self.available = Amount("{0:.8f} {1}".format(self.available, self.currency))
        if isinstance(self.total, Amount):
            self.total = Amount("{0:.8f} {1}".format(self.total.to_double(), self.currency))
        else:
            self.total = Amount("{0:.8f} {1}".format(self.total, self.currency))

