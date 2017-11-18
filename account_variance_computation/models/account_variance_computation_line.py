# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountVarianceComputationLine(models.Model):
    _name = "account.variance_computation_line"
    _description = "Variance Cost Computation Line"

    @api.multi
    @api.depends(
        "applied_account_id",
        "cost_allocation",
        "computation_id.period_id",
    )
    def _compute_cost(self):
        for line in self:
            applied_cost = over_variance = under_variance = 0.0
            computation = line.computation_id
            if computation.period_id:
                ctx = {
                    "period_from": computation.period_id.id,
                    "period_to": computation.period_id.id,
                }
                applied_cost = line.with_context(
                    ctx).applied_account_id.balance
            variance = abs(line.cost_allocation - applied_cost)
            if line.cost_allocation > line.applied_cost:
                under_variance = variance
            elif line.cost_allocation < line.applied_cost:
                over_variance = variance

            line.applied_cost = applied_cost
            line.over_variance = over_variance
            line.under_variance = under_variance

    computation_id = fields.Many2one(
        string="#Computation ID",
        comodel_name="account.variance_computation",
        ondelete="cascade",
    )
    applied_account_id = fields.Many2one(
        string="Applied Cost Account",
        comodel_name="account.account",
        required=True,
    )
    applied_cost = fields.Float(
        string="Applied Cost",
        digits=dp.get_precision('Account'),
        compute="_compute_cost",
        store=True,
    )
    under_variance = fields.Float(
        string="Under Variance",
        digits=dp.get_precision('Account'),
        compute="_compute_cost",
        store=True,
    )
    over_variance = fields.Float(
        string="Over Variance",
        digits=dp.get_precision('Account'),
        compute="_compute_cost",
        store=True,
    )
    cost_allocation = fields.Float(
        string="Cost Allocation",
        digits=dp.get_precision('Account'),
    )
    over_variance_account_id = fields.Many2one(
        string="Over Variance Account",
        comodel_name="account.account",
        required=True,
    )
    under_variance_account_id = fields.Many2one(
        string="Under Variance Account",
        comodel_name="account.account",
        required=True,
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
    )

    @api.multi
    def _check_variance(self):
        self.ensure_one()
        result = True
        if self.over_variance == self.under_variance == 0.0:
            result = False
        return result

    @api.multi
    def _prepare_account_move_line_data(self):
        self.ensure_one()
        account_id = self._get_variance_account_id()
        debit, credit = self._get_amount()
        result = []
        result.append((0, 0, {
            "name": self.computation_id.name,
            "account_id": account_id,
            "credit": credit,
            "debit": debit,
            "analytic_account_id": self.analytic_account_id and
            self.analytic_account_id.id or False,
        }))
        result.append((0, 0, {
            "name": self.computation_id.name,
            "account_id": self.applied_account_id.id,
            "debit": self.applied_cost,
            "credit": 0.0,
            "analytic_account_id": self.analytic_account_id and
            self.analytic_account_id.id or False,
        }))
        return result

    @api.multi
    def _get_variance_account_id(self):
        self.ensure_one()
        result = False
        if self.over_variance > 0:
            result = self.over_variance_account_id.id
        elif self.under_variance > 0:
            result = self.under_variance_account_id.id
        return result

    @api.multi
    def _get_amount(self):
        self.ensure_one()
        debit = credit = 0.0
        if self.over_variance > 0:
            credit = self.over_variance
            debit = 0.0
        elif self.under_variance > 0:
            debit = self.under_variance
            credit = 0.0
        return (debit, credit)
