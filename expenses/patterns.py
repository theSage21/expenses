import re
import pendulum
from collections import namedtuple


class NoMatch(Exception):
    pass


fields = ["debit_ac", "amount", "timestamp", "credit_ac", "txn"]
MSG = namedtuple("MSG", fields)
Pattern = namedtuple("Pattern", ["examples", "regex", "to_msg"])

PATTERNS = (
    Pattern(
        (
            """AD-ICICIB\n\nAcct XX440 debited with INR 120,000.00 on 30-Sep-20 & Acct XX221 credited. IMPS: 027409042496. Call 18002662 for dispute or SMS BLOCK 440 to 9215676766""",
        ),
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
)
