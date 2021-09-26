# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from ddt import data, ddt, unpack

from .base import BaseCase


@ddt
class TestOnchange(BaseCase):
    def test_prepaid_expense_amortization_onchange_move_line_id(self):
        values = {
            "type_id": self.type_amortization.id,
        }
        amortization = self.obj_amortization.new(values)
        amortization.onchange_move_line_id()
        self.assertEqual(amortization.move_line_id, self.obj_move_line)

    @data(
        ["prepaid_account1", "expense_account1"],
        ["prepaid_account2", "expense_account2"],
    )
    @unpack
    def test_prepaid_expense_amortization_onchange_contra_account_id(
        self, prepaid_account_name, expense_account_name
    ):
        prepaid_account = getattr(self, prepaid_account_name)
        expense_account = getattr(self, expense_account_name)
        payment, debit_line, credit_line = self._create_payment_receipt(
            direction="payment",
            partner=self.partner1,
            transaction_date=date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            journal=self.cash_journal,
            liquidity_account=self.cash_account,
            prepaid_account=prepaid_account,
            amount=1200.00,
        )
        values = {
            "type_id": self.type_amortization.id,
            "move_line_id": debit_line.id,
        }
        amortization = self.obj_amortization.new(values)
        amortization.onchange_contra_account_id()
        self.assertEqual(amortization.contra_account_id, expense_account)

    def test_prepaid_expense_amortization_onchange_journal_id(self):
        self.type_amortization.write(
            {
                "journal_id": self.amortization_journal.id,
            }
        )
        values = {
            "type_id": self.type_amortization.id,
        }
        amortization = self.obj_amortization.new(values)
        amortization.onchange_journal_id()
        self.assertEqual(amortization.journal_id, self.amortization_journal)

    @data([1, 2], [4, 3])
    @unpack
    def test_ddt(self, value1, value2):
        pass
