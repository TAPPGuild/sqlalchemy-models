"""
SQLAlchemy models
"""
import sqlalchemy as sa
from db import SABase


__all__ = ['User', 'UserKey', 'UserSetting', 'Setting', 'KeyPermission']


class User(SABase):
    """A User"""
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    createtime = sa.Column(sa.DateTime())
    address = sa.Column(sa.String(36), unique=True, nullable=False)
    username = sa.Column(sa.String(37), unique=True, nullable=False)

    def __repr__(self):
        return "<User(id=%s, username='%s', email='%s')>" % (
            self.id, self.username, self.address)


class UserKey(SABase):
    """A User's API key"""
    __tablename__ = "user_key"

    key = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    createtime = sa.Column(sa.DateTime(), nullable=False)
    deactivated_at = sa.Column(sa.DateTime())
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    permissionbits = sa.Column(sa.BigInteger)
    # TODO what is this Enum of? How to make in sqlalchemy?
    # keytype = sa.Column(sa.Enum())

    def __repr__(self):
        return "<UserKey(user_id=%s)>" % self.id


class UserSetting(SABase):
    """A Setting applied to a User"""
    __tablename__ = "user_setting"

    id = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    createtime = sa.Column(sa.DateTime(), nullable=False)
    deactivated_at = sa.Column(sa.DateTime())
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    setting_id = sa.Column("setting_id", sa.ForeignKey("setting.id"), nullable=False)
    # TODO what is a better way of storing settings of unknown type? Enum?
    value = sa.Column(sa.String(36), nullable=False)

    def __repr__(self):
        return "<User(id=%s, name='%s', value='%s')>" % (
            self.id, self.name, self.value)


class Setting(SABase):
    """A Setting"""
    __tablename__ = "setting"

    id = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(80), nullable=False)
    description = sa.Column(sa.String(320))
    # TODO what is this Enum of? How to make in sqlalchemy?
    # keytype = sa.Column(sa.Enum())

    def __repr__(self):
        return "<Setting(id=%s, name='%s')>" % (
            self.id, self.name)


class KeyPermission(SABase):
    """A Key Permission"""
    __tablename__ = "key_permission"

    permission = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(80), nullable=False)
    description = sa.Column(sa.String(320))

    def __repr__(self):
        return "<KeyPermission(permission=%s, name='%s')>" % (
            self.permission, self.name)

