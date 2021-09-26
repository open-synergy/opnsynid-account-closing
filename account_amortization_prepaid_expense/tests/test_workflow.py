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

    def action_create_schedule_no_error(self, amortization, prepaid_period):
        amortization.action_compute_amortization_schedule()
        self.assertEqual(len(amortization.schedule_ids), prepaid_period)

    def action_confirm_no_error(self, amortization):
        amortization.action_confirm()
        self.assertEqual(amortization.state, "confirm")

    def action_cancel_error(self, amortization):
        with self.assertRaises(UserError) as error_warning:
            amortization.action_cancel()
        err_msg = "Please cancel all aamortization schedule"
        self.assertEqual(error_warning.exception.message, tools.ustr(err_msg))
        self.assertNotEqual(amortization.state, "cancel")

    def action_cancel_no_error(self, amortization):
        amortization.action_cancel()
        self.assertEqual(amortization.state, "cancel")

    def action_restart_no_error(self, amortization):
        amortization.action_restart()
        self.assertEqual(amortization.state, "draft")

    def action_done_no_error(self, amortization):
        amortization.action_done()
        self.assertEqual(amortization.state, "done")

    def unlink_no_error(self, amortization):
        amortization.unlink()

    def unlink_error(self, amortization):
        with self.assertRaises(UserError) as error_warning:
            amortization.unlink()
        err_msg = "You can only delete data on draft state"
        self.assertEqual(error_warning.exception.message, tools.ustr(err_msg))

    def action_approve_no_error(self, amortization):
        amortization.restart_validation()
        self.assertEqual(
            amortization.definition_id.name, "Prepaid Expense Amortization - (test)"
        )
        amortization.invalidate_cache()
        amortization.validate_tier()
        self.assertTrue(amortization.validated)
        self.assertEqual(amortization.state, "open")

    def action_amortize_no_error(
        self, amortization, prepaid_period, amortization_schedule
    ):
        index = 0
        for schedule in amortization.schedule_ids:
            schedule.action_create_account_move()
            self.assertEqual(schedule.state, "post")
            self.assertEqual(
                schedule.amount, amortization_schedule[index]["amount_amortize"]
            )
            self.assertEqual(
                amortization.amount_residual,
                amortization_schedule[index]["amount_residual"],
            )
            index += 1

    def action_undo_amortize_no_error(self, amortization):
        for schedule in amortization.schedule_ids:
            schedule.action_remove_account_move()
            self.assertEqual(schedule.state, "draft")

    @file_data("scenario_prepaid.yaml")
    def test_prepaid_expense_amortization1(
        self, prepaid_amount, prepaid_period, amortization_schedule
    ):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error(prepaid_amount, prepaid_period)
        self.action_create_schedule_no_error(amortization, prepaid_period)
        self.action_confirm_no_error(amortization)
        self.action_approve_no_error(amortization)
        self.action_amortize_no_error(
            amortization, prepaid_period, amortization_schedule
        )
        self.action_done_no_error(amortization)

    @file_data("scenario_prepaid.yaml")
    def test_prepaid_expense_amortization2(
        self, prepaid_amount, prepaid_period, amortization_schedule
    ):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error(prepaid_amount, prepaid_period)
        self.action_create_schedule_no_error(amortization, prepaid_period)
        self.action_confirm_no_error(amortization)
        self.action_approve_no_error(amortization)
        self.action_amortize_no_error(
            amortization, prepaid_period, amortization_schedule
        )
        self.action_undo_amortize_no_error(amortization)
        self.action_cancel_no_error(amortization)
        self.action_restart_no_error(amortization)

    @file_data("scenario_prepaid.yaml")
    def test_prepaid_expense_amortization3(
        self, prepaid_amount, prepaid_period, amortization_schedule
    ):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error(prepaid_amount, prepaid_period)
        self.action_create_schedule_no_error(amortization, prepaid_period)
        self.action_confirm_no_error(amortization)
        self.unlink_error(amortization)

    @file_data("scenario_prepaid.yaml")
    def test_prepaid_expense_amortization4(
        self, prepaid_amount, prepaid_period, amortization_schedule
    ):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error(prepaid_amount, prepaid_period)
        self.unlink_no_error(amortization)

    @file_data("scenario_prepaid.yaml")
    def test_prepaid_expense_amortization5(
        self, prepaid_amount, prepaid_period, amortization_schedule
    ):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error(prepaid_amount, prepaid_period)
        self.action_create_schedule_no_error(amortization, prepaid_period)
        self.action_confirm_no_error(amortization)
        self.action_approve_no_error(amortization)
        self.action_amortize_no_error(
            amortization, prepaid_period, amortization_schedule
        )
        self.action_cancel_error(amortization)
        self.action_undo_amortize_no_error(amortization)
        self.action_cancel_no_error(amortization)
