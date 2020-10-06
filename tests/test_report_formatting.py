from expenses import const

const.DATABASE_URL = "sqlite:///:memory:"
const.TG_TOKEN = "dummy"
from expenses.bot import humanize


def test_amount_formatting():
    for amt, exp in [
        (10, "10    "),
        (1000, "1K    "),
        (1234, "1.23K "),
        (11234, "11.23K"),
        (88234, "88.23K"),
        (188234, "1.88L "),
        (8888234, "88.88L"),
    ]:
        assert humanize(amt) == exp
