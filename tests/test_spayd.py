from datetime import date, datetime

import pytest

from qrplatba import QRPlatbaGenerator


class TestIBANConversion:
    @pytest.mark.parametrize(
        "czech_account,expected_iban",
        [
            ("123456789/0123", "CZ2501230000000123456789"),
            ("12-123456789/0300", "CZ9403000000120123456789"),
            ("0000000001/0800", "CZ3408000000000000000001"),
            ("19-2000145399/0800", "CZ6508000000192000145399"),
        ],
    )
    def test_czech_to_iban(self, czech_account, expected_iban):
        generator = QRPlatbaGenerator(czech_account)
        text = generator.get_text()
        iban = text.split("ACC:")[1].split("*")[0]
        assert iban == expected_iban
        assert len(iban) == 24

    @pytest.mark.parametrize(
        "account",
        [
            "CZ6508000000192000145399",
            "SK3112000000198742637541",
        ],
    )
    def test_iban_passthrough(self, account):
        generator = QRPlatbaGenerator(account)
        assert f"ACC:{account}" in generator.get_text()


class TestGetText:
    @pytest.mark.parametrize(
        "kwargs,expected_parts,unexpected_parts",
        [
            (
                {"account": "CZ6508000000192000145399"},
                ["SPD*1.0*ACC:CZ6508000000192000145399"],
                ["*AM:", "*CC:", "*MSG:"],
            ),
            (
                {"account": "CZ6508000000192000145399", "amount": 450.00, "currency": "CZK"},
                ["ACC:CZ6508000000192000145399*", "AM:450.00", "CC:CZK"],
                [],
            ),
            (
                {
                    "account": "CZ6508000000192000145399",
                    "amount": 100.50,
                    "currency": "CZK",
                    "x_vs": 1234567890,
                    "x_ss": 1234,
                    "x_ks": 308,
                    "recipient_name": "Jan Novak",
                    "due_date": date(2025, 12, 31),
                    "message": "Test payment",
                },
                [
                    "AM:100.50*",
                    "CC:CZK*",
                    "X-VS:1234567890*",
                    "X-SS:1234*",
                    "X-KS:308",
                    "RN:Jan Novak*",
                    "DT:20251231*",
                    "MSG:Test payment",
                ],
                [],
            ),
        ],
    )
    def test_get_text(self, kwargs, expected_parts, unexpected_parts):
        generator = QRPlatbaGenerator(**kwargs)
        text = generator.get_text()
        for part in expected_parts:
            assert part in text, f"Expected {part!r} in {text!r}"
        for part in unexpected_parts:
            assert part not in text, f"Did not expect {part!r} in {text!r}"


class TestAmountFormatting:
    @pytest.mark.parametrize(
        "amount,expected",
        [
            (400.56, "AM:400.56"),
            (0, "AM:0.00"),
            (100, "AM:100.00"),
            (0.1, "AM:0.10"),
            (9999999.99, "AM:9999999.99"),
        ],
    )
    def test_amount_formatting(self, amount, expected):
        generator = QRPlatbaGenerator("CZ6508000000192000145399", amount=amount)
        assert expected in generator.get_text()


class TestDueDateFormatting:
    @pytest.mark.parametrize(
        "due_date,expected",
        [
            (date(2025, 3, 15), "DT:20250315"),
            (datetime(2025, 3, 15, 10, 30), "DT:20250315"),
            ("20250315", "DT:20250315"),
        ],
    )
    def test_due_date_formatting(self, due_date, expected):
        generator = QRPlatbaGenerator("CZ6508000000192000145399", due_date=due_date)
        assert expected in generator.get_text()


class TestFieldPresence:
    @pytest.mark.parametrize(
        "field,value,key",
        [
            ("x_vs", 0, "X-VS"),
            ("x_ss", 0, "X-SS"),
            ("x_ks", 0, "X-KS"),
            ("reference", 0, "RF"),
        ],
    )
    def test_zero_values_included(self, field, value, key):
        generator = QRPlatbaGenerator("CZ6508000000192000145399", **{field: value})
        assert f"{key}:{value}" in generator.get_text()

    @pytest.mark.parametrize(
        "field,key",
        [
            ("x_vs", "X-VS"),
            ("currency", "*CC"),
            ("message", "MSG"),
            ("recipient_name", "RN"),
        ],
    )
    def test_none_values_omitted(self, field, key):
        generator = QRPlatbaGenerator("CZ6508000000192000145399", **{field: None})
        assert f"{key}:" not in generator.get_text()


class TestAlternateAccounts:
    def test_alternate_accounts_mixed(self):
        generator = QRPlatbaGenerator(
            "CZ6508000000192000145399",
            alternate_accounts=["123456789/0800", "SK3112000000198742637541"],
        )
        text = generator.get_text()
        assert "ALT-ACC:" in text
        assert "SK3112000000198742637541" in text
        assert "/0800" not in text

    def test_alternate_accounts_single_iban(self):
        generator = QRPlatbaGenerator(
            "CZ6508000000192000145399",
            alternate_accounts=["CZ7508000000000123456789"],
        )
        text = generator.get_text()
        assert "ALT-ACC:CZ7508000000000123456789" in text
