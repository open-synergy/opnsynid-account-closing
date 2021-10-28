# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from ddt import ddt, file_data
from openerp import tools
from openerp.exceptions import Warning as UserError

from .base import BaseCase


@ddt
class TestPrepaidExpenseAmortization(BaseCase):
    def _create_no_error(self, prepaid_amount=0.0, prepaid_period=12):
        payment, debit_line, credit_line = self._create_payment_receipt(
            direction="payment",
            partner=self.partner1,
            transaction_date=date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            journal=self.cash_journal,
            liquidity_account=self.cash_account,
            prepaid_account=self.prepaid_account1,
            amount=prepaid_amount != 0.0 and prepaid_amount or 1200.00,
        )
        values = {
            "date": date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            "move_line_id": debit_line.id,
            "journal_id": self.amortization_journal.id,
            "contra_account_id": self.expense_account1.id,
            "date_start": date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            "period": "monthly",
            "period_number": prepaid_period,
        }
        amortization = self.obj_amortization.create(values)
        self.assertEqual(amortization.state, "draft")
        return amortization

    def action_create_schedule_no_error(self, amortization, attribute):
        prepaid_period = attribute["prepaid_period"]
        amortization.action_compute_amortization_schedule()
        self.assertEqual(len(amortization.schedule_ids), prepaid_period)

    def action_confirm_no_error(self, amortization, attribute):
        amortization.action_confirm()
        self.assertEqual(amortization.state, "confirm")

    def action_cancel_error(self, amortization, attribute):
        with self.assertRaises(UserError) as error_warning:
            amortization.action_cancel()
        err_msg = "Please cancel all aamortization schedule"
        self.assertEqual(error_warning.exception.message, tools.ustr(err_msg))
        self.assertNotEqual(amortization.state, "cancel")

    def action_cancel_no_error(self, amortization, attribute):
        amortization.action_cancel()
        self.assertEqual(amortization.state, "cancel")

    def action_restart_no_error(self, amortization, attribute):
        amortization.action_restart()
        self.assertEqual(amortization.state, "draft")

    def action_done_no_error(self, amortization, attribute):
        amortization.action_done()
        self.assertEqual(amortization.state, "done")

    def action_unlink_no_error(self, amortization, attribute):
        amortization.unlink()

    def action_unlink_error(self, amortization, attribute):
        with self.assertRaises(UserError) as error_warning:
            amortization.unlink()
        err_msg = "You can only delete data on draft state"
        self.assertEqual(error_warning.exception.message, tools.ustr(err_msg))

    def action_approve_no_error(self, amortization, attribute):
        amortization.restart_validation()
        self.assertEqual(
            amortization.definition_id.name, "Prepaid Expense Amortization - (test)"
        )
        amortization.invalidate_cache()
        amortization.validate_tier()
        self.assertTrue(amortization.validated)
        self.assertEqual(amortization.state, "open")

    def action_amortize_no_error(self, amortization, attribute):
        index = 0
        for schedule in amortization.schedule_ids:
            schedule.action_create_account_move()
            amount = round(
                schedule.amount, self.env["decimal.precision"].precision_get("Account")
            )
            self.assertEqual(schedule.state, "post")
            self.assertEqual(
                amount,
                attribute["amortization_schedule"][index]["amount_amortize"],
            )
            self.assertEqual(
                amortization.amount_residual,
                attribute["amortization_schedule"][index]["amount_residual"],
            )
            index += 1

    def action_undo_amortize_no_error(self, amortization, attribute):
        for schedule in amortization.schedule_ids:
            schedule.action_remove_account_move()
            self.assertEqual(schedule.state, "draft")

    @file_data("scenario_prepaid.yaml")
    def test_prepaid_expense_amortization(self, attribute, workflow_steps):
        prepaid_amount = attribute["prepaid_amount"]
        prepaid_period = attribute["prepaid_period"]
        amortization = self._create_no_error(prepaid_amount, prepaid_period)
        for workflow_step in workflow_steps:
            method_name = "action_" + workflow_step["name"]
            if workflow_step["error"]:
                method_name += "_error"
            else:
                method_name += "_no_error"
            method_to_run = getattr(self, method_name)
            method_to_run(amortization, attribute)
