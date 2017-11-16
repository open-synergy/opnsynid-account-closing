# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountVarianceComputationLine(models.Model):
    _name = "account.variance_computation_line"
    _description = "Variance Cost Computation Line"

    computation_id = fields.Many2one(
        string="#Computation ID",
        comodel_name="account.variance_computation"
    )
    applied_account_ids = fields.Char(
        string="Applied Account"
    )
    applied_cost = fields.Float(
        string="Applied Cost",
        digits=dp.get_precision('Account')
    )
    cost_allocation = fields.Float(
        string="Cost Allocation",
        digits=dp.get_precision('Account')
    )
    over_variance_account_id = fields.Many2one(
        string="Over Variance Account",
        comodel_name="account.account"
    )
    under_variance_account_id = fields.Many2one(
        string="Under Variance Account",
        comodel_name="account.account"
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account"
    )
    analytic_journal_id = fields.Many2one(
        string="Analytic Journal",
        comodel_name="account.analytic.journal"
    )

    @api.multi
    def _prepare_account_move_line_data(self):
        self.ensure_one()
        return True
