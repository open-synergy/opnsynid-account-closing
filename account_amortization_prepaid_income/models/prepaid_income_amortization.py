# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class PrepaidIncomeAmortization(models.Model):
    _name = "account.prepaid_income_amortization"
    _inherit = ["account.amortization_common"]
    _description = "Prepaid Income Amortization"

    @api.model
    def _default_type_id(self):
        return self.env.ref(
            "account_amortization_prepaid_income." "amortization_type_prepaid_income"
        ).id

    @api.multi
    @api.depends(
        "move_line_id",
        "move_line_id.account_id",
        "move_line_id.reconcile_id",
        "move_line_id.reconcile_partial_id",
    )
    def _compute_move_line(self):
        _super = super(PrepaidIncomeAmortization, self)
        _super._compute_move_line()

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_allowed_aml_ids(self):
        _super = super(PrepaidIncomeAmortization, self)
        _super._compute_allowed_aml_ids()

    schedule_ids = fields.One2many(
        string="Amortization Schedule",
        comodel_name="account.prepaid_income_amortization_schedule",
        inverse_name="amortization_id",
    )
    date = fields.Date(
        related="move_line_id.date",
        store=True,
    )

    type_id = fields.Many2one(
        default=lambda self: self._default_type_id(),
    )
