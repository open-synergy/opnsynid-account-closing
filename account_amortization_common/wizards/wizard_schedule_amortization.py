# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AmortizationScheduleConfirmationWizard(models.TransientModel):
    _name = "account.amortization_schedule_common.confirmation.wizard"
    _description = "account.amortization_schedule_common.confirmation.wizard"

    @api.model
    def _default_period_id(self):
        context = self.env.context
        ctx = dict(context or {}, account_period_prefer_normal=True)
        periods = self.env["account.period"].with_context(ctx).find()
        if periods:
            return periods[0]
        else:
            return False

    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
        domain=[("special", "=", False)],
        required=True,
        default=lambda self: self._default_period_id(),
        help="Choose the period for which you want to automatically "
        "post the amortization schedule lines",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="account.amortization_type",
        required=True,
    )

    @api.multi
    def get_amortization_type_object(self):
        self.ensure_one()
        result = False
        type_expense = self.env.ref(
            "account_amortization_prepaid_expense." "amortization_type_prepaid_expense"
        )
        if self.type_id.id == type_expense.id:
            result = self.env["account.prepaid_expense_amortization_schedule"]
        type_income = self.env.ref(
            "account_amortization_prepaid_income." "amortization_type_prepaid_income"
        )
        if self.type_id.id == type_income.id:
            result = self.env["account.prepaid_income_amortization_schedule"]
        return result

    @api.multi
    def amortization_schedule_compute(self):
        self.ensure_one()
        obj_account_amortization_schedule = self.get_amortization_type_object()
        start_period = self.period_id.date_start
        end_period = self.period_id.date_stop
        if obj_account_amortization_schedule is not False:
            schedule_ids = obj_account_amortization_schedule.search(
                [
                    ("state", "=", "draft"),
                    ("amortization_id.state", "=", "open"),
                    ("date", ">=", start_period),
                    ("date", "<=", end_period),
                ]
            )
            if schedule_ids:
                schedule_ids.action_create_account_move()
