from expenses import const

const.DATABASE_URL = "sqlite:///:memory:"
const.TG_TOKEN = "dummy"
from expenses.bot import parse, monthly_report, weekly_report
from expenses import db


def test_expenses_are_recorded():
    with db.session() as session:
        for sms in [
            """AX-HDFCBK

    ALERT:Rs.111.11 spent via Debit Card xx1111 at NETFLIX                   on Oct  1 1111 11:11PM without PIN/OTP.Not you?Call 11111111111.""",
            """VK-HDFCBK

    Rs 1111.11 debited from a/c **1111 on 11-11-11 to VPA 1111111111@okbizaxis(UPI Ref No 111111111111). Not you? Call on 11111111111 to report""",
            """VD-HDFCMF

    Your SIP Purchase in Folio 11111111/11 under HDFC Mid-Cap Opportunities Fund-Gr. for Rs. 1,111.11 has been processed at the NAV of 11.111 for 11.111 units .""",
            """VD-IPRUMF

    Dear Investor,Your SIP Purchase of Rs.1,111.11 in Folio 11111111/11 - Bluechip Fund - Growth for 11.111 units has been processed for NAV of 11.11 -IPRUMF
    """,
            """AD-ICICIB

    Acct XX111 debited with INR 111,111.11 on 11-Sep-11 & Acct XX111 credited. IMPS: 111111111111. Call 11111111 for dispute or SMS BLOCK 111 to 1111111111""",
            """JD-SBIINB

    Your a/c no. XXXXXXXX1111 is credited by Rs.111111.11 on 11-11-11 by a/c linked to mobile 1XXXXXX111-XXXXXXX XXXXXX (IMPS Ref no 111111111111). Download""",
            """AD-ICICIB

    Dear Customer, your Acct XX111 has been credited with INR 1,11,111.11 on 11-Sep-11. Info:INF*111111111111*SAL SEPT11. The Avbl Bal is INR 1,11,111.11""",
            """BW-SCISMS

    Your A/C XXXXX111111 Credited INR 111.11 on 11/11/11 -Deposit by transfer from Mr. XXXXXXXXXXXXX. Avl Bal INR 1,11,111.11""",
            """AD-HDFCBK

            ALERT:You've spent Rs.1111.11 via Debit Card xx1111 at www.hotstar.co on 1111-11-11:11:11:11.Avl Bal Rs.11111.11.Not you?Call 11111111111.""",
        ]:
            is_expense, amount = parse(sms)
            session.add(
                db.Message(
                    sms=sms,
                    is_expense=is_expense,
                    amount=amount,
                    is_parsed=True,
                )
            )
            session.commit()
    assert monthly_report() != []
    assert weekly_report() != []
