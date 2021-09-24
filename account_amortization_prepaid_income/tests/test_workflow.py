# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from openerp import tools
from openerp.exceptions import Warning as UserError
from openerp.tests.common import TransactionCase


class TestWorkflow(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestWorkflow, self).setUp(*args, **kwargs)
        self.obj_amortization = self.env["account.prepaid_income_amortization"]
        self.obj_move = self.env["account.move"]
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
        self.income_account1 = self.env.ref(
            "account_amortization_prepaid_income.demo_account3"
        )
        self.income_account2 = self.env.ref(
            "account_amortization_prepaid_income.demo_account4"
        )

        self.partner1 = self.env.ref("base.res_partner_2")

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

    def _create_no_error(self):
        payment = self._create_receipt()
        move_line = payment.line_id.filtered(lambda r: r.credit > 0.0)[0]
        values = {
            "date": date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            "move_line_id": move_line.id,
            "journal_id": self.amortization_journal.id,
            "contra_account_id": self.income_account1.id,
            "date_start": date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            "period": "monthly",
            "period_number": 12,
        }
        amortization = self.obj_amortization.create(values)
        self.assertEqual(amortization.state, "draft")
        return amortization

    def action_create_schedule_no_error(self, amortization):
        amortization.action_compute_amortization_schedule()
        self.assertEqual(len(amortization.schedule_ids), 12)

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
            amortization.definition_id.name, "Prepaid Income Amortization - (test)"
        )
        amortization.invalidate_cache()
        amortization.validate_tier()
        self.assertTrue(amortization.validated)
        self.assertEqual(amortization.state, "open")

    def action_amortize_no_error(self, amortization):
        for schedule in amortization.schedule_ids:
            schedule.action_create_account_move()
            self.assertEqual(schedule.state, "post")

    def action_undo_amortize_no_error(self, amortization):
        for schedule in amortization.schedule_ids:
            schedule.action_remove_account_move()
            self.assertEqual(schedule.state, "draft")

    def test_prepaid_income_amortization1(self):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error()
        self.action_create_schedule_no_error(amortization)
        self.action_confirm_no_error(amortization)
        self.action_approve_no_error(amortization)
        self.action_amortize_no_error(amortization)
        self.action_done_no_error(amortization)

    def test_prepaid_income_amortization2(self):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error()
        self.action_create_schedule_no_error(amortization)
        self.action_confirm_no_error(amortization)
        self.action_approve_no_error(amortization)
        self.action_amortize_no_error(amortization)
        self.action_undo_amortize_no_error(amortization)
        self.action_cancel_no_error(amortization)
        self.action_restart_no_error(amortization)

    def test_prepaid_income_amortization3(self):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error()
        self.action_create_schedule_no_error(amortization)
        self.action_confirm_no_error(amortization)
        self.unlink_error(amortization)

    def test_prepaid_income_amortization4(self):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error()
        self.unlink_no_error(amortization)

    def test_prepaid_income_amortization5(self):
        """
        create, confirm, approve, pay
        """
        amortization = self._create_no_error()
        self.action_create_schedule_no_error(amortization)
        self.action_confirm_no_error(amortization)
        self.action_approve_no_error(amortization)
        self.action_amortize_no_error(amortization)
        self.action_cancel_error(amortization)
        self.action_undo_amortize_no_error(amortization)
        self.action_cancel_no_error(amortization)
