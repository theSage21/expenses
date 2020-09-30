from . import patterns, db


def add_expense(sms):
    for _, reg, get_data in patterns.MAP:
        match = reg.match(sms)
        if match:
            msg = get_data(match)
            break
    else:
        raise patterns.NoMatch()
    # -----------
    with db.session() as session:
        dw = db.Wallet.getbyname(msg.debit_ac)
        cw = db.Wallet.getbyname(msg.credit_ac)
        txn = db.Transaction(
            amount=msg.amount,
            txid=msg.txn,
            sms=sms,
            debit_wallet_id=dw.id,
            credit_wallet_id=cw.id,
            txn_at=msg.timestamp,
        )
        session.add(txn)
        session.commit()
