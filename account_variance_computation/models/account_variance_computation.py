# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _

_STATE = [
    ("draft", "Draft"),
    ("confirmed", "Waiting for Approval"),
    ("approved", "Approved"),
    ("posted", "Posted"),
    ("cancelled", "Cancelled")
]


class AccountVarianceComputation(models.Model):
    _name = "account.variance_computation"
    _inherit = ["mail.thread"]
    _description = "Variance Cost Computation"

    @api.multi
    @api.depends(
        "real_cost_account_id",
        "period_id",
        "line_ids",
        "line_ids.cost_allocation",
    )
    def _compute_cost(self):
        for computation in self:
            real_cost = total_cost_allocation = allocation_diff = 0.0
            if computation.period_id:
                ctx = {
                    "period_from": computation.period_id.id,
                    "period_to": computation.period_id.id,
                }
                real_cost = computation.with_context(
                    ctx).real_cost_account_id.balance
            for line in computation.line_ids:
                total_cost_allocation += line.cost_allocation
            allocation_diff = real_cost - total_cost_allocation

            computation.real_cost = real_cost
            computation.total_cost_allocation = total_cost_allocation
            computation.allocation_diff = allocation_diff

    name = fields.Char(
        string="Name",
        required=True,
        default="/",
        readonly=True,
        copy=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_trx = fields.Date(
        string="Transaction Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        default=lambda self: self._default_date_trx(),
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    real_cost = fields.Float(
        String="Real Cost",
        digits=dp.get_precision('Account'),
        compute="_compute_cost",
        store=True,
        copy=False,
    )
    total_cost_allocation = fields.Float(
        string="Total Cost Allocation",
        digits=dp.get_precision('Account'),
        compute="_compute_cost",
        store=True,
        copy=False,
    )
    allocation_diff = fields.Float(
        string="Allocation Diff",
        digits=dp.get_precision('Account'),
        compute="_compute_cost",
        store=True,
    )
    note = fields.Text(
        string="Notes",
    )
    confirmed_date = fields.Datetime(
        string="Confirmation Date",
        readonly=True,
        copy=False,
    )
    confirmed_by = fields.Many2one(
        string="Confirmation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    approved_date = fields.Datetime(
        string="Approval Date",
        readonly=True,
        copy=False,
    )
    approved_by = fields.Many2one(
        string="Approval By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    posted_date = fields.Datetime(
        string="Post Date",
        readonly=True,
        copy=False,
    )
    posted_by = fields.Many2one(
        string="Post By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    cancelled_date = fields.Datetime(
        string="Cancellation Date",
        readonly=True,
        copy=False,
    )
    cancelled_by = fields.Many2one(
        string="Cancellation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    line_ids = fields.One2many(
        string="Cost Allocation",
        comodel_name="account.variance_computation_line",
        inverse_name="computation_id",
        readonly=True,
        copy=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move",
        readonly=True,
        ondelete="restrict",
        copy=False,
    )
    account_move_line_ids = fields.One2many(
        string="Move Lines",
        comodel_name="account.move.line",
        readonly=True,
        related="account_move_id.line_id",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    real_cost_account_id = fields.Many2one(
        string="Real Cost Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        readonly=True,
        default=lambda self: self._default_company_id(),
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    state = fields.Selection(
        string="State",
        selection=_STATE,
        readonly=True,
        default="draft",
    )

    @api.multi
    def button_action_draft(self):
        for computation in self:
            computation.write(
                computation._prepare_draft_data())

    @api.multi
    def button_action_confirm(self):
        for computation in self:
            computation.write(
                computation._prepare_confirm_data())

    @api.multi
    def button_action_approve(self):
        for computation in self:
            computation.write(
                computation._prepare_approve_data())

    @api.multi
    def button_action_post(self):
        for computation in self:
            computation.write(
                computation._prepare_post_data())

    @api.multi
    def button_action_cancel(self):
        for computation in self:
            move = computation.account_move_id
            computation.write(
                computation._prepare_cancel_data())
            move.unlink()

    @api.multi
    def _prepare_draft_data(self):
        self.ensure_one()
        result = {
            "confirmed_date": False,
            "confirmed_by": False,
            "approved_date": False,
            "approved_by": False,
            "posted_date": False,
            "posted_by": False,
            "cancelled_date": False,
            "cancelled_by": False,
            "state": "draft",
        }
        return result

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        result = {
            "confirmed_date": fields.Datetime.now(),
            "confirmed_by": self.env.user.id,
            "state": "confirmed",
        }
        return result

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        result = {
            "approved_date": fields.Datetime.now(),
            "approved_by": self.env.user.id,
            "state": "approved",
        }
        return result

    @api.multi
    def _prepare_post_data(self):
        self.ensure_one()
        move = self._create_account_move()
        result = {
            "posted_date": fields.Datetime.now(),
            "posted_by": self.env.user.id,
            "state": "posted",
            "account_move_id": move.id,
        }
        return result

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        result = {
            "cancelled_date": fields.Datetime.now(),
            "cancelled_by": False,
            "state": "cancelled",
            "account_move_id": False,
        }
        return result

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        move = self.env["account.move"].create(
            self._prepare_account_move_data())
        return move

    @api.multi
    def _prepare_account_move_data(self):
        self.ensure_one()
        data = {
            "name": self.name,
            "date": self.date_trx,
            "journal_id": self.journal_id.id,
            "period_id": self.period_id.id,
            "line_id": self._prepare_account_move_line_data(),
        }
        return data

    @api.multi
    def _prepare_account_move_line_data(self):
        self.ensure_one()
        result = []
        result.append(
            self._prepare_header_move_line())
        for line in self.line_ids:
            result += line._prepare_account_move_line_data()
        return result

    @api.multi
    def _prepare_header_move_line(self):
        self.ensure_one()
        result = (0, 0, {
            "name": self.name,
            "account_id": self.real_cost_account_id.id,
            "credit": self.real_cost,
            "debit": 0.0,
            "analytic_account_id": self.analytic_account_id and
            self.analytic_account_id.id or False,
        })
        return result

    @api.multi
    def _unlink_account_move(self):
        self.ensure_one()
        return True

    @api.model
    def _default_date_trx(self):
        return fields.Datetime.now()

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id

    @api.model
    def create(self, values):
        new_values = self._prepare_create_data(values)
        return super(AccountVarianceComputation, self).create(new_values)

    @api.model
    def _prepare_create_data(self, values):
        name = values.get("name", False)
        if not name or name == "/":
            values["name"] = self._create_sequence()
        return values

    @api.multi
    def _create_sequence(self):
        sequence = self.env.ref(
            "account_variance_computation.variance_seq")
        name = self.env["ir.sequence"].\
            next_by_id(sequence.id) or "/"
        return name

    @api.onchange("date_trx")
    def onchange_date_trx(self):
        pass

    @api.constrains(
        "state",
        "allocation_diff",
    )
    def _check_allocation_diff(self):
        if self.state == "confirmed" and self.allocation_diff > 0:
            raise UserError(
                _("There is still allocation difference"))

    @api.constrains(
        "state",
        "real_cost",
    )
    def _check_real_cost(self):
        if self.state == "confirmed" and self.real_cost <= 0:
            raise UserError(
                _("Real cost has to be greater than 0"))
