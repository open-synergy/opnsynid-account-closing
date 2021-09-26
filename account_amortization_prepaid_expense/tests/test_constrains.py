# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from datetime import date

from openerp import tools
from openerp.exceptions import ValidationError

from .base import BaseCase


class TestConstrains(BaseCase):
    def test_prepaid_expense_amortization_constrains_date_start(self):
        payment, debit_line, credit_line = self._create_payment_receipt(
            direction="payment",
            partner=self.partner1,
            transaction_date=date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            journal=self.cash_journal,
            liquidity_account=self.cash_account,
            prepaid_account=self.prepaid_account1,
            amount=1200.00,
        )
        values = {
            "move_line_id": debit_line.id,
            "journal_id": self.amortization_journal.id,
            "contra_account_id": self.expense_account1.id,
            "date_start": date(date.today().year - 1, 1, 1).strftime("%Y-%m-%d"),
            "period": "monthly",
            "period_number": 12,
        }
        with self.assertRaises(ValidationError) as error_warning:
            self.obj_amortization.create(values)
        err_msg = (
            "Error while validating constraint\n\n"
            "Date start has to be greater than effective date"
        )
        self.assertEqual(error_warning.exception.value, tools.ustr(err_msg))
