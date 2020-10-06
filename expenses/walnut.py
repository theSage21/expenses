import csv
import pendulum
from expenses import db


def import_walnut_report(path):
    "Import a walnut report to the database"
    with open(path, "r") as fl, db.session() as session:
        for row in csv.reader(fl):
            try:
                DATE, TIME, _, AMOUNT, _, EXPENSE, _, _, _ = row
                created_at = pendulum.from_format(f"{DATE} {TIME}", "DD-MM-YY HH:mm A")
            except ValueError:
                continue
            msg = db.Message(
                sms="",
                is_expense=EXPENSE == "Yes",
                is_imported=True,
                amount=int(float(AMOUNT.replace(",", ""))),
                created_at=created_at,
            )
            session.add(msg)  # pylint: disable=no-member
            print(msg.created_at, msg.amount, "imported")
        session.commit()  # pylint: disable=no-member
