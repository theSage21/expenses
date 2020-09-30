from . import patterns, db


def add_expense(sms):
    for _, reg, get_data in patterns.MAP:
        match = reg.match(sms)
        if match:
            msg = get_data(match)
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
                    is_parsed=True,
                )
                session.add(txn)
                session.commit()
            return
    with db.session() as session:
        txn = db.Transaction(
            sms=sms,
        )
        session.add(txn)
        session.commit()
    return
