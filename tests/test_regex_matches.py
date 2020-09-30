from expenses import patterns


def test_patterns():
    examples = {
        patterns.ICICI_IMPS: [
            """AD-ICICIB\n\nAcct XX440 debited with INR 120,000.00 on 30-Sep-20 & Acct XX221 credited. IMPS: 027409042496. Call 18002662 for dispute or SMS BLOCK 440 to 9215676766""",
        ]
    }
    for pat, exes in examples.items():
        reg, fn = patterns.MAP[pat]
        for ex in exes:
            match = reg.match(ex)
            assert match
            msg = fn(ex)
            assert msg
