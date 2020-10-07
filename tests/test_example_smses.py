from expenses import const

const.DATABASE_URL = "sqlite:///:memory:"
const.TG_TOKEN = "dummy"
from expenses.bot import parse, tag_message


def test_correct_expenses_are_recorded():
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
        assert is_expense and amount is not None, sms


def test_spam_is_ignored():
    for sms, has_amt in [
        (
            """BP-CHAYOS

            Chaayos is calling! Special weekend Offer-11% OFF on all your favorites.Valid on Dine in/Delivery!Use Code GJ11.Max Rs111 OFF on min bill Rs111 bit.ly/11wlb1G""",
            True,
        ),
        (
            """AD-ICICIB

            Dear Customer, Your Pre-Approved ICICI Bank Credit Card is just 1 steps away. As discussed with our executive, kindly log in to your account through Net""",
            False,
        ),
        (
            """AL-111111

            Cheer for your favorite team!
            Watch Dream11 IPL LIVE only on Disney+ Hotstar VIP
            Get 1 year subscription,1GB/day,UL calls for 11days at Rs111
            u.airtel.in/111""",
            True,
        ),
        (
            """JK-111111

            Want to watch Dream11 IPL on Disney+ Hotstar VIP?
            Get Rs.111 Jio Cricket Plan and watch LIVE CRICKET MATCHES
            Recharge NOW https://rb.gy/1xvfyy""",
            True,
        ),
        (
            """11011011

            Arriving today: Naturalis Essence of Nature Peppermint Essential Oil ... will be delivered by AmzAgent(+111111111111 PIN 1111). Track: https://amzn.in/d/aDBWTR1""",
            False,
        ),
        (
            """BW-600500

            Level up your game! Avail special offers on exclusive gaming accessories only at HP World Stores- Vaishali Nagar, 111111111111. Unsub:https://bit.ly/2HNmWlB""",
            False,
        ),
    ]:
        is_expense, amount = parse(sms)
        assert not is_expense, sms
        found_amt = amount is not None
        assert found_amt == has_amt, sms


def test_tags():
    for sms, expected in [
        (
            """AX-HDFCBK

    ALERT:Rs.111.11 spent via Debit Card xx1111 at NETFLIX                   on Oct  1 1111 11:11PM without PIN/OTP.Not you?Call 11111111111.""",
            {"bank.HDFC", "card.xx1111", "vendor.NETFLIX"},
        ),
        (
            """VK-HDFCBK

    Rs 1111.11 debited from a/c **1111 on 11-11-11 to VPA 1111111111@okbizaxis(UPI Ref No 111111111111). Not you? Call on 11111111111 to report""",
            {"bank.HDFC", "upi.1111111111@okbizaxis", "dac.**1111"},
        ),
        (
            """VD-HDFCMF

    Your SIP Purchase in Folio 11111111/11 under HDFC Mid-Cap Opportunities Fund-Gr. for Rs. 1,111.11 has been processed at the NAV of 11.111 for 11.111 units .""",
            {"bank.HDFC"},
        ),
        (
            """VD-IPRUMF

    Dear Investor,Your SIP Purchase of Rs.1,111.11 in Folio 11111111/11 - Bluechip Fund - Growth for 11.111 units has been processed for NAV of 11.11 -IPRUMF""",
            {
                "bank.IPRUMF",
            },
        ),
        (
            """AD-ICICIB

    Acct XX111 debited with INR 111,111.11 on 11-Sep-11 & Acct XX111 credited. IMPS: 111111111111. Call 11111111 for dispute or SMS BLOCK 111 to 1111111111""",
            {"bank.ICICI", "dac.XX111", "cac.XX111"},
        ),
        (
            """JD-SBIINB

    Your a/c no. XXXXXXXX1111 is credited by Rs.111111.11 on 11-11-11 by a/c linked to mobile 1XXXXXX111-XXXXXXX XXXXXX (IMPS Ref no 111111111111). Download""",
            {
                "bank.SBI",
                "cac.XXXXXXXX1111",
            },
        ),
        (
            """AD-ICICIB

    Dear Customer, your Acct XX111 has been credited with INR 1,11,111.11 on 11-Sep-11. Info:INF*111111111111*SAL SEPT11. The Avbl Bal is INR 1,11,111.11""",
            {"bank.ICICI", "cac.XX111"},
        ),
        (
            """BW-SCISMS

    Your A/C XXXXX111111 Credited INR 111.11 on 11/11/11 -Deposit by transfer from Mr. XXXXXXXXXXXXX. Avl Bal INR 1,11,111.11""",
            {"cac.XXXXX111111"},
        ),
        (
            """AD-HDFCBK

            ALERT:You've spent Rs.1111.11 via Debit Card xx1111 at www.hotstar.co on 1111-11-11:11:11:11.Avl Bal Rs.11111.11.Not you?Call 11111111111.""",
            {"bank.HDFC", "card.xx1111", "vendor.www.hotstar.co"},
        ),
    ]:
        tags = tag_message(sms)
        assert tags == expected, sms


def test_multiple_matches():
    for sms in [
        """AD-HDFCBK

    ALERT:You've spent Rs.1111.11 via Debit Card xx7211 at AMAZON on 2020-10-06:08:21:43.Avl Bal Rs.11111.11.Not you?Call 18002586161."""
    ]:
        is_expense, amount = parse(sms)
        assert is_expense and amount == "1111.11"
