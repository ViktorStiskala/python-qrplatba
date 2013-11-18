# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime, date
import re
import qrcode
from qrplatba.svg import QRPlatbaSVGImage


class QRPlatbaGenerator:
    RE_ACCOUNT = re.compile(r'(?P<ba>\d+(?=-))?(?P<a>\d+)/(?P<b>\d{4})')

    def __init__(self, account, amount=None, currency=None, x_vs=None, x_ss=None, x_ks=None, alternate_accounts=None, recipient_name=None,
                 due_date=None, payment_type=None, message=None, notification_type=None, notification_address=None, x_per=None, x_id=None,
                 x_url=None, reference=None):
        """
        http://qr-platba.cz/pro-vyvojare/specifikace-formatu/

        :param account: ACC account number, can be specified either as IBAN or in CZ commonly used format 12-123456789/0300
        :param amount: AM payment amount
        :param currency: CC currency (3 digits)
        :param x_vs: X-VS
        :param x_ss: X-SS
        :param x_ks: X-KS
        :param alternate_accounts: ALT-ACC
        :param recipient_name: RN recipient name
        :param due_date: DT due date, IS0 8601
        :param payment_type: PT max 3 digits
        :param message: MSG message for recipient, max 60 chars
        :param notification_type: NT P for phone or E for email
        :param notification_address: NTA
        :param x_per: X-PER number of days to repeat payment if unsuccessful
        :param x_id: X-ID
        :param x_url: X-URL
        :param reference: RF recipient reference number. Max 16 digits. integer.
        """
        self.account = account
        self.amount = amount
        self.currency = currency
        self.x_vs = x_vs
        self.x_ss = x_ss
        self.x_ks = x_ks
        self.alternate_accounts = alternate_accounts
        self.recipient_name = recipient_name
        self.due_date = due_date
        self.payment_type = payment_type
        self.message = message
        self.notification_type = notification_type
        self.notification_address = notification_address
        self.x_per = x_per
        self.x_id = x_id
        self.x_url = x_url
        self.reference = reference

    def _convert_to_iban(self, account):
        """
        Convert czech account number to IBAN
        """
        acc = self.RE_ACCOUNT.match(account)
        iban = 'CZ00{b}{ba:0>6}{a:0>10}'.format(
            ba=acc.group('ba') or 0,
            a=acc.group('a'),
            b=acc.group('b'),
        )

        # convert IBAN letters into numbers
        crc = re.sub(r'[A-Z]', lambda m: str(ord(m.group(0)) - 55), iban[4:] + iban[:4])

        # compute control digits
        digits = "{:0>2}".format(98 - int(crc) % 97)

        return iban[:2] + digits + iban[4:]

    @property
    def _account(self):
        if self.account is not None:
            out = 'ACC:{}*'

            if self.RE_ACCOUNT.match(self.account):
                return out.format(self._convert_to_iban(self.account))
            return out.format(self.account)
        return ""

    @property
    def _alternate_accounts(self):
        if self.alternate_accounts is not None:
            formatted = []
            for account in self.alternate_accounts:
                if self.RE_ACCOUNT.match(account):
                    formatted.append(self._convert_to_iban(account))
                else:
                    formatted.append(account)
            return "ALT-ACC:{}*".format(','.join(formatted))
        return ''

    @property
    def _amount(self):
        if self.amount is not None:
            return "AM:{:.2f}*".format(self.amount)
        return ""

    @property
    def _due_date(self):
        if self.due_date is not None:
            str_part = 'DT:{}*'
            if isinstance(self.due_date, datetime):
                return str_part.format(self.due_date.date().isoformat()).replace('-', '')
            if isinstance(self.due_date, date):
                return str_part.format(self.due_date.isoformat()).replace('-', '')
            return str_part.format(self.due_date)
        return ''

    def _format_item_string(self, item, name):
        if item is not None:
            return "{name}:{value}*".format(name=name, value=item)
        return ''

    def get_text(self):
        return "SPD*1.0*{ACC}{ALTACC}{AM}{CC}{RF}{RN}{DT}{PT}{MSG}{NT}{NTA}{XPER}{XVS}{XSS}{XKS}{XID}{XURL}".format(
            ACC=self._account,
            ALTACC=self._alternate_accounts,
            AM=self._amount,
            CC=self._format_item_string(self.currency, 'CC'),
            RF=self._format_item_string(self.reference, 'RF'),
            RN=self._format_item_string(self.recipient_name, 'RN'),
            DT=self._due_date,
            PT=self._format_item_string(self.payment_type, 'PT'),
            MSG=self._format_item_string(self.message, 'MSG'),
            NT=self._format_item_string(self.notification_type, 'NT'),
            NTA=self._format_item_string(self.notification_address, 'NTA'),
            XPER=self._format_item_string(self.x_per, 'X-PER'),
            XVS=self._format_item_string(self.x_vs, 'X-VS'),
            XSS=self._format_item_string(self.x_ss, 'X-SS'),
            XKS=self._format_item_string(self.x_ks, 'X-KS'),
            XID=self._format_item_string(self.x_id, 'X-ID'),
            XURL=self._format_item_string(self.x_url, 'X-URL')
        ).rstrip('*')

    def make_image(self, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M):
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            image_factory=QRPlatbaSVGImage,
            border=border,
        )
        qr.add_data(self.get_text())
        qr.make(fit=True)

        return qr.make_image()
