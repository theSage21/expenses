from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    DateTime,
    Integer,
    Boolean,
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


# Each transaction must be linked to a wallet
class Message(Base):
    __tablename__ = "message"
    id = Column("id", Integer, primary_key=True)
    is_parsed = Column("is_parsed", Boolean, default=False, nullable=False)
    is_expense = Column("is_expense", Boolean, default=None)
    sms = Column("sms", String, nullable=False)
    tags = Column("tags", String)
    amount = Column("amount", Integer)
    created_at = Column("created_at", DateTime, default=utcnow)


Base.metadata.create_all(engine)
