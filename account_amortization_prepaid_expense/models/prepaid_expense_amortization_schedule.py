# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class PrepaidExpenseAmortizationSchedule(models.Model):
    _name = "account.prepaid_expense_amortization_schedule"
    _inherit = [
        "account.amortization_schedule_common"
    ]
    _description = "Prepaid Expense Amortization Schedule"

    @api.multi
    def _compute_amortization_state(self):
        _super = super(PrepaidExpenseAmortizationSchedule, self)
        _super._compute_amortization_state()

    amortization_id = fields.Many2one(
        string="Amortization",
        comodel_name="account.prepaid_expense_amortization",
    )
    move_id = fields.Many2one(
        related="move_line_id.move_id",
    )
