# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _


class AccountAmortizationScheduleCommon(models.AbstractModel):
    _name = "account.amortization_schedule_common"
    _description = "Abstract Model for Amortization Schedule"

    @api.multi
    def _compute_amortization_state(self):
        for document in self:
            document.amortization_state = \
                document.amortization_id.state

    amortization_id = fields.Many2one(
        string="Amortization",
        comodel_name="account.amortization_common",
        ondelete="cascade",
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    amount = fields.Float(
        string="Amount",
        required=True,
    )
    move_line_id = fields.Many2one(
        string="Move Line",
        comodel_name="account.move.line",
        readonly=True,
    )
    move_id = fields.Many2one(
        string="# Move",
        comodel_name="account.move",
        readonly=True,
    )
    amortization_state = fields.Selection(
        string="Amortization State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        readonly=True,
        compute="_compute_amortization_state",
        store=False,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("post", "Posted"),
        ],
        required=True,
        default="draft",
    )

    @api.multi
    def action_create_account_move(self):
        for document in self:
            document._create_account_move()
            document.write({
                "state": "post",
            })
            if document.amortization_id._check_done():
                document.amortization_id.action_done()

    @api.multi
    def action_remove_account_move(self):
        for document in self:
            document._remove_account_move()
            document.write({
                "state": "draft",
            })

    @api.multi
    def _remove_account_move(self):
        self.ensure_one()
        aml = self.amortization_id.move_line_id
        reconcile = aml.reconcile_id or aml.reconcile_partial_id or False
        if reconcile:
            move_lines = reconcile.line_id
            move_lines -= self.move_line_id
            reconcile.unlink()

            if len(move_lines) >= 2:
                move_lines.reconcile_partial()
        move = self.move_id
        self.write({"move_line_id": False})
        move.unlink()

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        obj_move = self.env["account.move"]
        obj_aml = self.env["account.move.line"]
        aml_to_be_reconcile = self.amortization_id.move_line_id
        move = obj_move.create(self._prepare_account_move())
        aml = obj_aml.create(self._prepare_amortization_aml(move))
        self.write({"move_line_id": aml.id})
        aml_to_be_reconcile += aml
        obj_aml.create(self._prepare_contra_amortization_aml(move))
        aml_to_be_reconcile.reconcile_partial()
        return move

    @api.multi
    def _prepare_account_move(self):
        self.ensure_one()
        amortization = self.amortization_id
        obj_period = self.env["account.period"]
        period_id = obj_period.find(self.date)[0].id
        return {
            "journal_id": amortization.journal_id.id,
            "date": self.date,
            "period_id": period_id,
        }

    @api.multi
    def _prepare_amortization_aml(self, move):
        self.ensure_one()
        debit, credit = self._get_aml_amount()
        amortization = self.amortization_id
        partner_id = amortization.move_line_id.partner_id and \
            amortization.move_line_id.partner_id.id or \
            False
        analytic_id = amortization.move_line_id.analytic_account_id and \
            amortization.move_line_id.analytic_account_id.id or \
            False
        return {
            "move_id": move.id,
            "name": _("Amortization"),
            "account_id": amortization.account_id.id,
            "debit": debit,
            "credit": credit,
            "partner_id": partner_id,
            "analytic_account_id": analytic_id,
        }

    @api.multi
    def _prepare_contra_amortization_aml(self, move):
        self.ensure_one()
        debit, credit = self._get_aml_amount(True)
        amortization = self.amortization_id
        analytic_id = amortization.analytic_id and \
            amortization.analytic_id.id or \
            False
        return {
            "move_id": move.id,
            "name": _("Amortization"),
            "account_id": amortization.contra_account_id.id,
            "debit": debit,
            "credit": credit,
            "analytic_account_id": analytic_id,
        }

    @api.multi
    def _get_aml_amount(self, contra=False):
        self.ensure_one()
        amortization = self.amortization_id
        direction = amortization.type_id.direction
        debit = credit = 0.0
        if direction == "dr":
            credit = self.amount
        else:
            debit = self.amount

        if contra:
            debit, credit = credit, debit

        return debit, credit

    @api.model
    def cron_create_account_move(self):
        date_now = fields.Date.today()
        schedule_ids = self.search([
            ("amortization_id.state", "=", "open"),
            ("date", "=", date_now),
            ("state", "=", "draft")
        ])
        if schedule_ids:
            for schedule in schedule_ids:
                schedule.action_create_account_move()
