#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : sikai.zhang
# @Time    : 5/24/19 9:41 AM
# this file must be put in the same dir as database-*.yaml
import database
from database import Base
from sqlalchemy import Integer, Column, String, Float

session_cls = database.sessions['acid']
engine = database.engines['acid']

class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(Integer)
    balance = Column(Integer)

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def to_dict(self):
        return {
            'balance': self.balance,
            'owner': self.owner
        }


class ATM():

    def open_account(self, owner_id):
        account = Account(owner_id)
        session = session_cls()
        session.add(account)
        session.commit()

    def transfer(self, fro, to, amount):
        with engine.connect() as trx:
            trx.execute("UPDATE account set balance = balance - {} where owner = {}".format(amount, fro))
            trx.execute("UPDATE account set balance = balance + {} where owner = {}".format(amount, to))

    def save(self, owner, amount):
        with engine.connect() as trx:
            trx.execute("UPDATE account set balance = balance + {} where owner = {}".format(amount, owner))


def do():
    atm = ATM()
    for i in range(101, 200):
        atm.open_account(i)


def consistency_check():
    pass


if __name__ == '__main__':
    account1 = Account(1)
    account2 = Account(2)
    s = session_cls()
    s.add(account1)
    s.add(account2)
    s.commit()
    # s.rollback()
