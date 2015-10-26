"""
SQLAlchemy models
"""
import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

SABase = declarative_base()

__all__ = ['User', 'UserKey', 'UserSetting', 'Setting', 'KeyPermission']


class User(SABase):
    """A User"""
    __tablename__ = "user"
    __name__ = "user"

    id = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True,
                   doc="primary key")
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    address = sa.Column(sa.String(36), unique=True, nullable=False)
    username = sa.Column(sa.String(37), unique=True, nullable=False)

    def __repr__(self):
        return "<User(id=%s, username='%s', email='%s')>" % (
            self.id, self.username, self.address)


class UserKey(SABase):
    """A User's API key"""
    __tablename__ = "user_key"
    __name__ = "user_key"

    key = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True, 
                    doc="primary key")
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    deactivated_at = sa.Column(sa.DateTime(), nullable=True)
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    permissionbits = sa.Column(sa.BigInteger, nullable=True)
    # TODO what is this Enum of? How to make in sqlalchemy?
    # keytype = sa.Column(sa.Enum())
    keytype = sa.Column(sa.String(36), nullable=False)

    def __repr__(self):
        return "<UserKey(user_id=%s, keytype='%s')>" % (self.user_id,
                                                        self.keytype)


class UserSetting(SABase):
    """A Setting applied to a User"""
    __tablename__ = "user_setting"
    __name__ = "user_setting"

    id = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True,
                   doc="primary key")
    createtime = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    deactivated_at = sa.Column(sa.DateTime())
    user_id = sa.Column("user_id", sa.ForeignKey("user.id"), nullable=False)
    user = orm.relationship("User")
    setting_id = sa.Column("setting_id", sa.ForeignKey("setting.id"), nullable=False)
    setting = orm.relationship("Setting")
    # TODO what is a better way of storing settings of unknown type? Enum?
    value = sa.Column(sa.String(36), nullable=False)

    def __repr__(self):
        return "<User(id=%s, name='%s', value='%s')>" % (
            self.id, self.name, self.value)


class Setting(SABase):
    """A Setting"""
    __tablename__ = "setting"
    __name__ = "setting"

    id = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True,
                   doc="primary key")
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
    __name__ = "key_permission"

    permission = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True,
                           doc="primary key")
    name = sa.Column(sa.String(80), nullable=False)
    description = sa.Column(sa.String(320))

    def __repr__(self):
        return "<KeyPermission(permission=%s, name='%s')>" % (
            self.permission, self.name)

