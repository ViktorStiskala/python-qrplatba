from datetime import date, datetime

import pytest

from qrplatba import QRPlatbaGenerator


class TestIBANConversion:
    """Czech account numbers must be correctly converted to IBAN; existing IBANs pass through."""

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
    """SPAYD string generation with various field combinations."""

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
    """Amounts must be formatted with exactly two decimal places."""

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
    """Due dates must be formatted as YYYYMMDD regardless of input type."""

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
    """Zero values must be included in the output; None values must be omitted."""

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
        "field,value,key",
        [
            ("payment_type", "IP", "PT"),
            ("notification_type", "E", "NT"),
            ("notification_address", "test@example.com", "NTA"),
            ("x_per", 7, "X-PER"),
            ("x_id", "ABCDEF", "X-ID"),
            ("x_url", "https://example.com", "X-URL"),
        ],
    )
    def test_optional_fields_included(self, field, value, key):
        generator = QRPlatbaGenerator("CZ6508000000192000145399", **{field: value})
        assert f"{key}:{value}" in generator.get_text()

    @pytest.mark.parametrize(
        "field,key",
        [
            ("x_vs", "X-VS"),
            ("currency", "*CC"),  # prefixed with * to avoid matching the "ACC:" field
            ("message", "MSG"),
            ("recipient_name", "RN"),
        ],
    )
    def test_none_values_omitted(self, field, key):
        generator = QRPlatbaGenerator("CZ6508000000192000145399", **{field: None})
        assert f"{key}:" not in generator.get_text()


class TestAlternateAccounts:
    """Alternate accounts must be converted to IBAN and included as ALT-ACC fields."""

    def test_alternate_accounts_mixed(self):
        generator = QRPlatbaGenerator(
            "CZ6508000000192000145399",
            alternate_accounts=["123456789/0800", "SK3112000000198742637541"],
        )
        text = generator.get_text()
        assert "ALT-ACC:" in text
        assert "SK3112000000198742637541" in text
        assert "/0800" not in text

    def test_empty_alternate_accounts_omitted(self):
        generator = QRPlatbaGenerator("CZ6508000000192000145399", alternate_accounts=[])
        assert "ALT-ACC" not in generator.get_text()

    def test_alternate_accounts_single_iban(self):
        generator = QRPlatbaGenerator(
            "CZ6508000000192000145399",
            alternate_accounts=["CZ7508000000000123456789"],
        )
        text = generator.get_text()
        assert "ALT-ACC:CZ7508000000000123456789" in text


class TestBIC:
    """BIC/SWIFT code must be appended to ACC with + separator."""

    def test_iban_with_bic(self):
        generator = QRPlatbaGenerator("CZ5855000000001265098001", bic="RZBCCZPP")
        assert "ACC:CZ5855000000001265098001+RZBCCZPP" in generator.get_text()

    def test_czech_account_with_bic(self):
        generator = QRPlatbaGenerator("123456789/0123", bic="RZBCCZPP")
        text = generator.get_text()
        assert "+RZBCCZPP" in text
        assert "/0123" not in text

    def test_no_bic(self):
        generator = QRPlatbaGenerator("CZ5855000000001265098001")
        assert "+" not in generator.get_text().split("ACC:")[1].split("*")[0]


class TestBackwardCompatibility:
    """Verify all documented and expected import paths and API patterns still work."""

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    @pytest.mark.parametrize(
        "import_statement,attr",
        [
            ("from qrplatba import QRPlatbaGenerator", "QRPlatbaGenerator"),
            ("from qrplatba import SpaydGenerator", "SpaydGenerator"),
            ("from qrplatba.generator import QRPlatbaGenerator", "QRPlatbaGenerator"),
            ("from qrplatba.spayd import SpaydGenerator", "SpaydGenerator"),
            ("from qrplatba.spayd import QRPlatbaGenerator", "QRPlatbaGenerator"),
        ],
    )
    def test_import_paths(self, import_statement, attr):
        ns = {}
        exec(import_statement, ns)  # noqa: S102
        assert attr in ns

    def test_deprecated_spayd_import_warns(self):
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from qrplatba.spayd import QRPlatbaGenerator  # noqa: F401, F811

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "qrplatba.spayd" in str(w[0].message)

    def test_qrplatba_generator_inherits_spayd(self):
        from qrplatba import QRPlatbaGenerator, SpaydGenerator

        assert issubclass(QRPlatbaGenerator, SpaydGenerator)

    def test_qrplatba_generator_has_get_text(self):
        generator = QRPlatbaGenerator("CZ6508000000192000145399")
        text = generator.get_text()
        assert text.startswith("SPD*1.0*")

    def test_qrplatba_generator_has_make_image(self):
        generator = QRPlatbaGenerator("CZ6508000000192000145399")
        img = generator.make_image()
        assert hasattr(img, "save")
        assert hasattr(img, "to_string")

    def test_image_is_svg_subclass(self):
        from qrcode.image.svg import SvgFragmentImage, SvgPathImage

        img = QRPlatbaGenerator("CZ6508000000192000145399").make_image()
        assert isinstance(img, SvgPathImage)
        assert isinstance(img, SvgFragmentImage)

    def test_save_positional_kind(self, tmp_path):
        img = QRPlatbaGenerator("CZ6508000000192000145399").make_image()
        filename = tmp_path / "test.svg"
        img.save(filename, "SVG")
        assert filename.exists()

    def test_to_string_encoding(self):
        img = QRPlatbaGenerator("CZ6508000000192000145399").make_image()
        svg_data = img.to_string(encoding="unicode")
        assert isinstance(svg_data, str)
        assert "QR platba" in svg_data
