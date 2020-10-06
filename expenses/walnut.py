import csv
import pendulum
from expenses import db


def import_walnut_report(path):
    "Import a walnut report to the database"
    with open(path, "r") as fl, db.session() as session:
        for row in csv.reader(fl):
            try:
                DATE, TIME, PLACE, AMOUNT, ACCOUNT, EXPENSE, CATEGORY, TAGS, NOTE = row
                created_at = pendulum.from_format(f"{DATE} {TIME}", "DD-MM-YY HH:mm A")
            except ValueError:
                continue
            msg = db.Message(
                sms="Walnut import",
                is_expense=EXPENSE == "Yes",
                amount=int(float(AMOUNT.replace(",", ""))),
                created_at=created_at,
            )
            session.add(msg)
            print(msg.created_at, msg.amount, "imported")
        session.commit()
