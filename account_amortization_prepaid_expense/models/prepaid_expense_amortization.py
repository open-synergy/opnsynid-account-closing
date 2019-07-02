# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class PrepaidExpenseAmortization(models.Model):
    _name = "account.prepaid_expense_amortization"
    _inherit = [
        "account.amortization_common"
    ]
    _description = "Prepaid Expense Amortization"

    @api.model
    def _default_type_id(self):
        return self.env.ref(
            "account_amortization_prepaid_expense."
            "amortization_type_prepaid_expense").id

    @api.multi
    @api.depends(
        "move_line_id",
        "move_line_id.account_id",
        "move_line_id.reconcile_id",
        "move_line_id.reconcile_partial_id",
    )
    def _compute_move_line(self):
        _super = super(PrepaidExpenseAmortization, self)
        _super._compute_move_line()

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_allowed_aml_ids(self):
        _super = super(PrepaidExpenseAmortization, self)
        _super._compute_allowed_aml_ids()

    schedule_ids = fields.One2many(
        string="Amortization Schedule",
        comodel_name="account.prepaid_expense_amortization_schedule",
        inverse_name="amortization_id",
    )
    date = fields.Date(
        related="move_line_id.date",
        store=True,
    )

    type_id = fields.Many2one(
        default=lambda self: self._default_type_id(),
    )
