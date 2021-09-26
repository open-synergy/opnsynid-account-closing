# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class BaseCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(BaseCase, self).setUp(*args, **kwargs)
        self.obj_amortization = self.env["account.prepaid_expense_amortization"]
        self.obj_move = self.env["account.move"]
        self.obj_move_line = self.env["account.move.line"]
        self.obj_period = self.env["account.period"]
        self.cash_journal = self.env.ref("account.cash_journal")
        self.amortization_journal = self.env.ref(
            "account_amortization_prepaid_expense.demo_journal1"
        )

        self.cash_account = self.env.ref("account.cash")
        self.prepaid_account1 = self.env.ref(
            "account_amortization_prepaid_expense.demo_account1"
        )
        self.prepaid_account2 = self.env.ref(
            "account_amortization_prepaid_expense.demo_account2"
        )
        self.expense_account1 = self.env.ref(
            "account_amortization_prepaid_expense.demo_account3"
        )
        self.expense_account2 = self.env.ref(
            "account_amortization_prepaid_expense.demo_account4"
        )

        self.partner1 = self.env.ref("base.res_partner_2")

        self.type_amortization = self.env.ref(
            "account_amortization_prepaid_expense.amortization_type_prepaid_expense"
        )

        return result

    def _create_payment_receipt(
        self,
        direction,
        partner,
        transaction_date,
        journal,
        liquidity_account,
        prepaid_account,
        amount,
    ):
        period_id = self.obj_period.find(transaction_date).id
        if direction == "receipt":
            debit_account = liquidity_account
            credit_account = prepaid_account
        else:
            debit_account = prepaid_account
            credit_account = liquidity_account

        values = {
            "date": transaction_date,
            "journal_id": journal.id,
            "period_id": period_id,
        }
        move = self.obj_move.create(values)
        debit_line = self._create_payment_receipt_line(
            "debit", move, debit_account, partner, amount
        )
        credit_line = self._create_payment_receipt_line(
            "credit", move, credit_account, partner, amount
        )
        return move, debit_line, credit_line

    def _create_payment_receipt_line(self, line_type, move, account, partner, amount):
        value = {
            "name": "test move line",
            "move_id": move.id,
            "account_id": account.id,
            "partner_id": partner.id,
            "debit": line_type == "debit" and amount or 0.0,
            "credit": line_type == "credit" and amount or 0.0,
        }
        return self.obj_move_line.create(value)
