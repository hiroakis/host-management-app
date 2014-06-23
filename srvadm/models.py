from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy.orm import relation, backref
from sqlalchemy.dialects.mysql import (
    INTEGER,
    TINYINT,
    VARCHAR,
    DATETIME,
)
from datetime import datetime

from srvadm import db

class Role(db.Model):
    __tablename__ = 'role'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8',
    }

    role_name = Column('role_name', VARCHAR(length=64),
        primary_key=True,
        autoincrement=False)

    @classmethod
    def get_all(cls, query):
        return query(cls).all()

    @classmethod
    def get_one(cls, query, role_name):
        return query(cls).filter(cls.role_name == role_name).first()

    @classmethod
    def get_in_role_names(cls, query, role_names):
        return query(cls).filter(cls.role_name.in_(role_names)).all()


class IP(db.Model):
    __tablename__ = 'ip'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8',
    }

    ip = Column('ip', VARCHAR(length=64),
        primary_key=True,
        autoincrement=False)
    is_used = Column('is_used', TINYINT(unsigned=True),
        server_default='0',
        nullable=False)

    @classmethod
    def get_all(cls, query):
        return query(cls).all()

    @classmethod
    def get_used(cls, query):
        return query(cls).filter(cls.is_used == 1).all()

    @classmethod
    def get_unused(cls, query):
        return query(cls).filter(cls.is_used == 0).all()

    @classmethod
    def get_one(cls, query, ipaddr):
        return query(cls).filter(cls.ip == ipaddr).first()


class Host(db.Model):
    __tablename__ = 'host'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8',
    }

    id = Column('id', INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True)
    host_name = Column('host_name', VARCHAR(length=64),
        unique=True,
        nullable=True)
    ip = Column('ip', VARCHAR(length=64),
        ForeignKey('ip.ip', onupdate='cascade'))
    created_at = Column('created_at', DATETIME,
        default=datetime.now(),
        nullable=False)
    updated_at = Column('updated_at', DATETIME,
        default=datetime.now(),
        nullable=False)
    role = relation('RoleMap', backref='host', cascade='all, delete', uselist=True)

    @classmethod
    def get_all(cls, query):
        return query(cls).all()

    @classmethod
    def get_one_by_ip(cls, query, ip):
        return query(cls).filter(cls.ip == ip).first()

    @classmethod
    def get_one_by_host_name(cls, query, host_name):
        return query(cls).filter(cls.host_name == host_name).first()

    @classmethod
    def get_in_host_names(cls, query, host_names):
        return query(cls).filter(cls.host_name.in_(host_names)).all()

Index('idx_hostName', Host.host_name)

class RoleMap(db.Model):
    __tablename__ = 'role_map'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8',
    }

    id = Column('id', INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True)
    host_name = Column('host_name', VARCHAR(length=64),
        ForeignKey('host.host_name', onupdate='cascade', ondelete='cascade'),
        nullable=False)
    role_name = Column('role_name', VARCHAR(length=64),
        ForeignKey('role.role_name', onupdate='cascade'),
        nullable=False)

    @classmethod
    def get_by_role_name(cls, query, role_name):
        return query(cls).filter(cls.role_name == role_name).all()

    @classmethod
    def get_one_by_role_name(cls, query, role_name):
        return query(cls).filter(cls.role_name == role_name).first()

    @classmethod
    def get_by_host_name(cls, query, host_name):
        return query(cls).filter(cls.host_name == host_name).all()

    @classmethod
    def get_by_host_name_and_role_name(cls, query, host_name, role_name):
        return query(cls).filter(cls.host_name == host_name).filter(cls.role_name == role_name).first()

