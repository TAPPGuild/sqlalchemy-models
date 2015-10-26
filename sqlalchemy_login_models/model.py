"""
SQLAlchemy models
"""
import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

SABase = declarative_base()

__all__ = ['User', 'UserKey', 'IntUserSetting', 'StrUserSetting',
           'DateTimeUserSetting', 'Setting', 'KeyPermission']


class User(SABase):
    """A User"""
    __tablename__ = "user"
    __name__ = __tablename__

    id = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True,
                   doc="primary key")
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    username = sa.Column(sa.String(37), unique=True, nullable=False)
    # optionally generated on server and given to client for pre-send hashing
    salt = sa.Column(sa.String(12), unique=True)

    def __repr__(self):
        return "<User(id=%s, username='%s', email='%s')>" % (
            self.id, self.username, self.address)


class UserKey(SABase):
    """A User's API key"""
    __tablename__ = "user_key"
    __name__ = __tablename__

    id = sa.Column(sa.Integer, sa.Sequence('user_key_id_seq'), primary_key=True,
                   doc="primary key")
    key = sa.Column(sa.String(36), unique=True, nullable=False)
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    deactivated_at = sa.Column(sa.DateTime(), nullable=True)
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    permissionbits = sa.Column(sa.BigInteger, nullable=True)
    keytype = sa.Column(sa.Enum("public", "tfa"))
    # algorithm?
    last_nonce = sa.Column(sa.Integer, nullable=False, default=0)

    def __repr__(self):
        return "<UserKey(user_id=%s, keytype='%s')>" % (self.user_id,
                                                        self.keytype)


class KeyPermission(SABase):
    """A Key Permission"""
    __tablename__ = "key_permission"
    __name__ = __tablename__

    id = sa.Column(sa.Integer, sa.Sequence('key_permission_id_seq'), primary_key=True,
               doc="primary key")

    permission = sa.Column(sa.BigInteger, nullable=False)
    name = sa.Column(sa.String(80), nullable=False)
    description = sa.Column(sa.String(320))

    def __repr__(self):
        return "<KeyPermission(permission=%s, name='%s')>" % (
            self.permission, self.name)


# TODO do we want a pivot table for all User Settings?

#class UserSetting(SABase):
#    """A mixin for UserSetting classes"""
#    __tablename__ = "user_setting"
#    __name__ = __tablename__
#
#    id = sa.Column(sa.Integer, sa.Sequence('user_setting_id_seq'),
#                   primary_key=True, doc="primary key")
#    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
#    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
#    setting_name = sa.Column("setting_name", sa.ForeignKey("setting.name"), 
#                             nullable=False)


class IntUserSetting(SABase):
    """An Int Setting applied to a User"""
    __tablename__ = "int_user_setting"

    id = sa.Column(sa.Integer, sa.Sequence('user_int_setting_id_seq'),
                   primary_key=True, doc="primary key")
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    setting_name = sa.Column("setting_name", sa.ForeignKey("setting.name"), 
                             nullable=False)
    value = sa.Column(sa.Integer, nullable=False)

    def __repr__(self):
        return "<User(id=%s, setting_name='%s', value=%s)>" % (
            self.id, self.setting_name, self.value)


class StrUserSetting(SABase):
    """A Setting applied to a User"""
    __tablename__ = "str_user_setting"

    id = sa.Column(sa.Integer, sa.Sequence('user_str_setting_id_seq'),
                   primary_key=True, doc="primary key")
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    setting_name = sa.Column("setting_name", sa.ForeignKey("setting.name"), 
                             nullable=False)
    value = sa.Column(sa.String(320), nullable=False)

    def __repr__(self):
        return "<User(id=%s, setting_name='%s', value='%s')>" % (
            self.id, self.setting_name, self.value)


class DateTimeUserSetting(SABase):
    """A Setting applied to a User"""
    __tablename__ = "date_time_user_setting"

    id = sa.Column(sa.Integer, sa.Sequence('user_date_time_setting_id_seq'), 
                   primary_key=True, doc="primary key")
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    setting_name = sa.Column("setting_name", sa.ForeignKey("setting.name"), 
                             nullable=False)
    value = sa.Column(sa.DateTime(), nullable=False)

    def __repr__(self):
        return "<User(id=%s, setting_name='%s', value='%s')>" % (
            self.id, self.setting_name, self.value)


class Setting(SABase):
    """A Setting"""
    __tablename__ = "setting"
    __name__ = __tablename__

    name = sa.Column(sa.String(80), primary_key=True)
    description = sa.Column(sa.String(320))
    value_type = sa.Column(sa.Enum("str", "int", "date-time"))

    def __repr__(self):
        return "<Setting(id=%s, name='%s')>" % (
            self.id, self.name)

