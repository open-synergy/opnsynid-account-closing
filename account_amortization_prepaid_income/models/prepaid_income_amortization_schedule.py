# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class PrepaidIncomeAmortizationSchedule(models.Model):
    _name = "account.prepaid_income_amortization_schedule"
    _inherit = ["account.amortization_schedule_common"]
    _description = "Prepaid Income Amortization Schedule"

    @api.multi
    def _compute_amortization_state(self):
        _super = super(PrepaidIncomeAmortizationSchedule, self)
        _super._compute_amortization_state()

    @api.multi
    @api.depends(
        "manual",
        "move_id",
    )
    def _compute_state(self):
        _super = super(PrepaidIncomeAmortizationSchedule, self)
        _super._compute_state()

    amortization_id = fields.Many2one(
        string="Amortization",
        comodel_name="account.prepaid_income_amortization",
    )
    move_id = fields.Many2one(
        related="move_line_id.move_id",
    )
