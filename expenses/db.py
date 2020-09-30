from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
)
import pendulum
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from . import const

engine = create_engine(const.DATABASE_URL)
Base = declarative_base()
newSession = sessionmaker(engine)
sessStack = []


def utcnow():
    return pendulum.now("UTC")


def sess():
    global sessStack
    return sessStack[-1]


@contextmanager
def session():
    global sessStack
    s = newSession()
    sessStack.append(s)
    try:
        yield s
    finally:
        popped = sessStack.pop(-1)
        assert popped == s
        s.close()


# Identifies a place that the user spends money at.
class Vendor(Base):
    __tablename__ = "vendor"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)


# Multiple modes of payment can be attached to a single vendor
class Wallet(Base):
    __tablename__ = "wallet"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    vendor_id = Column("vendor_id", Integer, ForeignKey("vendor.id"), nullable=True)

    @staticmethod
    def getbyname(name):
        s = sess()
        wal = s.query(Wallet).filter(Wallet.name == name).first()
        if wal is None:
            wal = Wallet(name=name)
            s.add(wal)
            s.commit()
        return wal


# Each transaction must be linked to a wallet
class Transaction(Base):
    __tablename__ = "transaction"
    id = Column("id", Integer, primary_key=True)
    amount = Column("amount", Integer)
    txid = Column("txid", String)
    sms = Column("sms", String)
    debit_wallet_id = Column("debit_wallet_id", Integer, ForeignKey("wallet.id"))
    credit_wallet_id = Column("credit_wallet_id", Integer, ForeignKey("wallet.id"))
    created_at = Column("created_at", DateTime, default=utcnow)
    txn_at = Column("txn_at", DateTime)
    tags = Column("tags", String)


Base.metadata.create_all(engine)
