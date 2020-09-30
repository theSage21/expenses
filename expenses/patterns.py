import re
import pendulum
from collections import namedtuple


class NoMatch(Exception):
    pass


fields = ["debit_ac", "amount", "timestamp", "credit_ac", "txn"]
MSG = namedtuple("MSG", fields)
Pattern = namedtuple("Pattern", ["examples", "regex", "to_msg"])

ICICI_IMPS = "iimps"

MAP = {
    ICICI_IMPS: (
        re.compile(
            r"AD-ICICIB\n+Acct (\S+) debited with INR (\S+) on (\S+) & Acct (\S+) credited. IMPS: (\d+).*"
        ),
        lambda x: MSG(
            debit_ac=x.group(1),
            amount=x.group(2),
            timestamp=pendulum.from_format(x.group(3), "DD-MMM-YY"),
            credit_ac=x.group(4),
            txn=x.group(5),
        ),
    ),
}
