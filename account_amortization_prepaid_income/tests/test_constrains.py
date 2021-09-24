# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from openerp import tools
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestConstrains(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestConstrains, self).setUp(*args, **kwargs)
        self.obj_amortization = self.env["account.prepaid_income_amortization"]
        self.obj_move = self.env["account.move"]
        self.obj_move_line = self.env["account.move.line"]
        self.obj_period = self.env["account.period"]
        self.cash_journal = self.env.ref("account.cash_journal")
        self.amortization_journal = self.env.ref(
            "account_amortization_prepaid_income.demo_journal1"
        )

        self.cash_account = self.env.ref("account.cash")
        self.prepaid_account1 = self.env.ref(
            "account_amortization_prepaid_income.demo_account1"
        )
        self.prepaid_account2 = self.env.ref(
            "account_amortization_prepaid_income.demo_account2"
        )
        self.revenue_account1 = self.env.ref(
            "account_amortization_prepaid_income.demo_account3"
        )
        self.revenue_account2 = self.env.ref(
            "account_amortization_prepaid_income.demo_account4"
        )

        self.partner1 = self.env.ref("base.res_partner_2")

        self.type_amortization = self.env.ref(
            "account_amortization_prepaid_income.amortization_type_prepaid_income"
        )

        return result

    def _create_receipt(self):
        values = {
            "date": date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            "journal_id": self.cash_journal.id,
            "period_id": self.obj_period.find().id,
            "line_id": [
                (
                    0,
                    0,
                    {
                        "name": "test prepaid",
                        "account_id": self.cash_account.id,
                        "debit": 1200.00,
                        "partner_id": self.partner1.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "test prepaid",
                        "account_id": self.prepaid_account1.id,
                        "credit": 1200.00,
                        "partner_id": self.partner1.id,
                    },
                ),
            ],
        }
        return self.obj_move.create(values)

    def test_prepaid_income_amortization_constrains_date_start(self):
        payment = self._create_receipt()
        move_line = payment.line_id.filtered(lambda r: r.credit > 0.0)[0]
        values = {
            "move_line_id": move_line.id,
            "journal_id": self.amortization_journal.id,
            "contra_account_id": self.revenue_account1.id,
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
