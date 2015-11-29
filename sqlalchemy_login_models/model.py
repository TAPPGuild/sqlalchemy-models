"""
SQLAlchemy models
"""
import datetime
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import (Column, Sequence, Integer, String, DateTime, BigInteger,
                        Enum, ForeignKey)
from . import Base

__all__ = ['User', 'UserKey', 'IntUserSetting',
           'StrUserSetting', 'DateTimeUserSetting', 'Setting', 'KeyPermission']


class User(Base):
    """A User"""

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True,
                doc="primary key")
    createtime = Column(DateTime(), default=datetime.datetime.utcnow)
    username = Column(String(37), unique=True, nullable=False)

    # optionally generated on server and given to client for pre-send hashing
    salt = Column(String(12), unique=True)

    def __repr__(self):
        return "<User(id=%s, username='%s')>" % (
            self.id, self.username)


class UserKey(Base):
    """A User's API key"""

    id = Column(Integer, Sequence('user_key_id_seq'), primary_key=True,
                doc="primary key")
    key = Column(String(36), unique=True, nullable=False)
    createtime = Column(DateTime(), default=datetime.datetime.utcnow)
    deactivated_at = Column(DateTime(), nullable=True)
    permissionbits = Column(BigInteger, nullable=True)
    keytype = Column(Enum("public", "tfa"), nullable=False)
    last_nonce = Column(Integer, nullable=False, default=0)
    # algorithm column?

    # relationships
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = orm.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return "<UserKey(user_id=%s, keytype='%s')>" % (self.user_id,
                                                        self.keytype)


class KeyPermission(Base):
    """A Key Permission"""

    id = Column(Integer, Sequence('key_permission_id_seq'),
                primary_key=True, doc="primary key")

    permission = Column(BigInteger, nullable=False)
    name = Column(String(80), nullable=False)
    description = Column(String(320))

    user_key_id = Column(Integer, ForeignKey("user_key.id"), nullable=False)
    user_key = orm.relationship("UserKey", foreign_keys=[user_key_id])

    def __repr__(self):
        return "<KeyPermission(user_key_id=%s, permission=%s, name='%s')>" % (
            self.user_key_id, self.permission, self.name)


class UserSetting(object):
    """A mixin for UserSetting classes"""

    createtime = Column(DateTime(), default=datetime.datetime.utcnow)
    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey("user.id"),
                         nullable=False, name='user_id')
    #user = orm.relationship("User", foreign_keys=[user_id])

    @declared_attr
    def setting_name(cls):
        return Column(Integer, ForeignKey("setting.name"),
                         nullable=False, name='setting_name')
    #setting = orm.relationship("Setting", foreign_keys=[setting_name])


class IntUserSetting(Base, UserSetting):
    """An Int Setting applied to a User"""

    id = Column(Integer, Sequence('user_int_setting_id_seq'),
                   primary_key=True, doc="primary key")
    value = Column(Integer, nullable=False)

    def __repr__(self):
        return "<IntUserSetting(id=%s, setting_name='%s', value=%s)>" % (
            self.id, self.setting_name, self.value)


class StrUserSetting(Base, UserSetting):
    """A Setting applied to a User"""

    id = Column(Integer, Sequence('user_str_setting_id_seq'),
                   primary_key=True, doc="primary key")
    value = Column(String(320), nullable=False)

    def __repr__(self):
        return "<StrUserSetting(id=%s, setting_name='%s', value='%s')>" % (
            self.id, self.setting_name, self.value)


class DateTimeUserSetting(Base, UserSetting):
    """A Setting applied to a User"""

    id = Column(Integer, Sequence('user_date_time_setting_id_seq'),
                   primary_key=True, doc="primary key")
    value = Column(DateTime(), nullable=False)

    def __repr__(self):
        return "<DateTimeUserSetting(id=%s, setting_name='%s', value='%s')>" % (
            self.id, self.setting_name, self.value)


class Setting(Base):
    """A Setting"""

    name = Column(String(80), primary_key=True)
    description = Column(String(320))
    value_type = Column(Enum("str", "int", "date-time"))

    def __repr__(self):
        return "<Setting(id=%s, name='%s')>" % (
            self.id, self.name)

