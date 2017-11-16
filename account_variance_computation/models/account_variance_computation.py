# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

STATE = [
    ("draft", "Draft"),
    ("confirmed", "Waiting for Approval"),
    ("approved", "Approved"),
    ("posted", "Posted"),
    ("cancelled", "Cancelled")
]


class AccountVarianceComputation(models.Model):
    _name = "account.variance_computation"
    _description = "Variance Cost Computation"

    name = fields.Char(
        string="Name",
        required=True
    )
    date_trx = fields.Date(
        string="Transaction Date",
        required=True
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period"
    )
    real_cost = fields.Float(
        String="Real Cost",
        digits=dp.get_precision('Account')
    )
    total_cost_allocation = fields.Float(
        string="Total Cost Allocation",
        digits=dp.get_precision('Account')
    )
    note = fields.Text(
        string="Notes"
    )
    confirmed_date = fields.Date(
        string="Confirmation Date"
    )
    confirmed_by = fields.Many2one(
        string="Confirmation By",
        comodel_name="res.users"
    )
    approved_date = fields.Date(
        string="Approval Date"
    )
    approved_by = fields.Many2one(
        string="Approval By",
        comodel_name="res.users"
    )
    posted_date = fields.Date(
        string="Post Date"
    )
    posted_by = fields.Many2one(
        string="Post By",
        comodel_name="res.users"
    )
    cancelled_date = fields.Date(
        string="Cancellation Date"
    )
    cancelled_by = fields.Many2one(
        string="Cancellation By",
        comodel_name="res.users"
    )
    cost_allocation_ids = fields.Char(
        string="Cost Allocation"
    )
    account_move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move"
    )
    account_move_line_ids = fields.Char(
        string="Move Lines",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal"
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account"
    )
    analytic_journal_id = fields.Many2one(
        string="Analytic Journal",
        comodel_name="account.analytic.journal"
    )
    state = fields.Selection(
        string="State",
        selection=STATE
    )

    @api.multi
    def button_action_draft(self):
        return True

    @api.multi
    def button_action_confirm(self):
        return True

    @api.multi
    def button_action_approve(self):
        return True

    @api.multi
    def button_action_post(self):
        return True

    @api.multi
    def button_action_cancel(self):
        return True

    @api.multi
    def _prepare_draft_data(self):
        self.ensure_one()
        return True

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return True

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        return True

    @api.multi
    def _prepare_post_data(self):
        self.ensure_one()
        return True

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return True

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        return True

    @api.multi
    def _prepare_account_move_data(self):
        self.ensure_one()
        return True

    @api.multi
    def _prepare_account_move_line_data(self):
        self.ensure_one()
        return True

    @api.multi
    def _unlink_account_move(self):
        self.ensure_one()
        return True

    @api.model
    def _default_date_trx(self):
        return True

    @api.model
    def _prepare_create_data(self):
        return True

    @api.model
    def _create_sequence(self):
        return True

    @api.onchage("date_trx")
    def onchange_date_trx(self):
        return True
