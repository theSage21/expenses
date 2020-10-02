from . import patterns, db
import re

# Possible formats in which the amount could be expressed
AMOUNTS = [
    re.compile(s)
    for s in [r".*INR[^\d]*(\S+).*" r".*Rs[^\d]*(\S+).*", r".*RS[^\d]*(\S+).*"]
]


def add_expense(sms):
    amount = None
    for rgx in AMOUNTS:
        amount = rgx.match(sms)
        if amount:
            break
    with db.session() as session:
        if amount is None:
            msg = db.Message(sms=sms)
        else:
            msg = db.Message(
                amount=amount.group(1), sms=sms, is_parsed=True, is_expense=True
            )
        session.add(msg)
        session.commit()
