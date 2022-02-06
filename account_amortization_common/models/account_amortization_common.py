# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)

try:
    import numpy as np
    import pandas as pd
except (ImportError, IOError) as err:  # pragma: no cover
    _logger.debug(err)


class AccountAmortizationCommon(models.AbstractModel):
    _name = "account.amortization_common"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
        "base.cancel.reason_common",
        "tier.validation",
    ]
    _state_from = ["draft", "confirm"]
    _state_to = ["open"]
    _description = "Abstract Model for Amortization"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.multi
    def _compute_allowed_aml_ids(self):
        obj_aml = self.env["account.move.line"]
        for document in self:
            account_ids = []
            amortization_type = document.type_id
            for mapping in amortization_type.account_mapping_ids:
                account_ids.append(mapping.account_id.id)
            criteria = [
                ("account_id", "in", account_ids),
                ("reconcile_id", "=", False),
                ("reconcile_partial_id", "=", False),
            ]
            if amortization_type.direction == "dr":
                criteria.append(("debit", ">", 0.0))
            else:
                criteria.append(("credit", ">", 0.0))
            amls = obj_aml.search(criteria)
            document.allowed_move_line_ids = [(6, 0, amls.ids)]

    @api.multi
    def _compute_move_line(self):
        for document in self:
            aml = document.move_line_id
            residual = amortized = 0.0

            currency_id = (
                aml.currency_id
                and aml.currency_id.id
                or document.company_id.currency_id.id
            )

            for line in document.schedule_ids.filtered(
                lambda r: r.state in ["post", "manual"]
            ):
                amortized += line.amount

            residual = document.amount - amortized

            document.amount_residual = residual
            document.currency_id = currency_id

    name = fields.Char(
        string="# Document",
        default="/",
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
        default=lambda self: self._default_company_id(),
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        compute="_compute_move_line",
        store=True,
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="account.amortization_type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    source = fields.Selection(
        string="Source",
        selection=[
            ("move", "Journal Entry"),
            ("manual", "Manual"),
        ],
        default="move",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    move_line_id = fields.Many2one(
        string="Move Line",
        comodel_name="account.move.line",
        required=False,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_move_line_ids = fields.Many2many(
        string="Allowed Move Lines",
        comodel_name="account.move.line",
        compute="_compute_allowed_aml_ids",
    )
    account_id = fields.Many2one(
        string="Amortization Account",
        comodel_name="account.account",
        compute=False,
        store=True,
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    contra_account_id = fields.Many2one(
        string="Amortization Contra Account",
        comodel_name="account.account",
        domain=[
            ("type", "=", "other"),
        ],
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    analytic_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        domain=[
            ("type", "=", "general"),
        ],
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date = fields.Date(
        string="Transaction Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_start = fields.Date(
        string="Start Amortization",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    period = fields.Selection(
        string="Period",
        selection=[
            ("monthly", "Monthly"),
        ],
        default="monthly",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    period_number = fields.Integer(
        string="Period Number",
        default=1,
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    schedule_ids = fields.One2many(
        string="Amortization Schedule",
        comodel_name="account.amortization_schedule_common",
        inverse_name="amortization_id",
    )
    amount = fields.Float(
        string="Amount",
        compute=False,
        store=True,
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    amount_residual = fields.Float(
        string="Amount Residual",
        compute="_compute_move_line",
        store=True,
    )
    note = fields.Text(
        string="Note",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
    )

    # Log Fields
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
    )
    confirm_user_id = fields.Many2one(
        string="Confirmed By",
        comodel_name="res.users",
        readonly=True,
    )
    cancel_date = fields.Datetime(
        string="Cancel Date",
        readonly=True,
    )
    cancel_user_id = fields.Many2one(
        string="Cancelled By",
        comodel_name="res.users",
        readonly=True,
    )

    # Policy Field
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
    )
    restart_validation_ok = fields.Boolean(
        string="Can Restart Validation",
        compute="_compute_policy",
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
    )

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())
            document._compute_amortization_schedule()
            document.request_validation()

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())

    @api.multi
    def action_done(self):
        for document in self:
            document.write(document._prepare_done_data())

    @api.multi
    def action_cancel(self):
        msg = _("Please cancel all aamortization schedule")
        for document in self:
            if not document._check_cancel():
                raise UserError(msg)
            document.write(document._prepare_cancel_data())
            document.restart_validation()
            document.schedule_ids.unlink()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

    @api.multi
    def _prepare_confirm_data(self):
        return {
            "state": "confirm",
            "confirm_date": fields.Datetime.now(),
            "confirm_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_approve_data(self):
        return {
            "state": "open",
        }

    @api.multi
    def _prepare_done_data(self):
        return {
            "state": "done",
        }

    @api.multi
    def _prepare_cancel_data(self):
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_restart_data(self):
        return {
            "state": "draft",
            "confirm_date": False,
            "confirm_user_id": False,
            "approve_date": False,
            "approve_user_id": False,
            "cancel_date": False,
            "cancel_user_id": False,
        }

    @api.onchange("type_id")
    def onchange_move_line_id(self):
        self.move_line_id = False

    @api.onchange("move_line_id", "type_id")
    def onchange_contra_account_id(self):
        self.contra_account_id = False
        if self.move_line_id:
            obj_mapping = self.env["account.amortization_type_account_mapping"]
            criteria = [
                ("type_id", "=", self.type_id.id),
                ("account_id", "=", self.account_id.id),
            ]
            mappings = obj_mapping.search(criteria)
            if len(mappings) > 0:
                self.contra_account_id = mappings[0].contra_account_id.id

    @api.onchange("type_id")
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id.journal_id:
            self.journal_id = self.type_id.journal_id.id

    @api.onchange("source", "move_line_id")
    def onchange_account_id(self):
        self.account_id = False
        if self.source == "move" and self.move_line_id:
            ml = self.move_line_id
            self.account_id = ml.account_id

    @api.onchange("source", "move_line_id")
    def onchange_date(self):
        self.date = False
        if self.source == "move" and self.move_line_id:
            ml = self.move_line_id
            self.date = ml.date

    @api.onchange("source", "move_line_id")
    def onchange_amount(self):
        self.amount = 0.0
        if self.source == "move" and self.move_line_id:
            ml = self.move_line_id
            if ml.debit > 0.0:
                self.amount = ml.debit
            elif ml.credit > 0.0:
                self.amount = ml.credit

    @api.multi
    def _check_done(self):
        self.ensure_one()
        result = False
        if self.amount_residual == 0:
            result = True
        return result

    @api.multi
    def _check_cancel(self):
        self.ensure_one()
        result = True
        obj_schedule = self.env[self._get_amortization_schedule_name()]
        criteria = [
            ("state", "in", ["post", "manual"]),
            ("amortization_id", "=", self.id),
        ]
        post_count = obj_schedule.search_count(criteria)
        if post_count > 0:
            result = False
        return result

    @api.constrains(
        "move_line_id",
        "date_start",
    )
    def constrains_date_start(self):
        if self.move_line_id and self.date_start:
            if self.move_line_id.date > self.date_start:
                msg = _("Date start has to be greater than effective date")
                raise UserError(msg)

    @api.constrains(
        "move_line_id",
        "state",
    )
    def constrains_no_duplicate_aml(self):
        if self.state not in ["draft", "cancel"]:
            obj_amortization = self.env[str(self._model)]
            criteria = [
                ("move_line_id", "=", self.move_line_id.id),
                ("id", "!=", self.id),
                ("state", "not in", ["draft", "cancel"]),
            ]
            count_amr = obj_amortization.search_count(criteria)
            if count_amr > 0:
                msg = _("Same move line can not use more than once")
                raise UserError(msg)

    @api.multi
    def action_compute_amortization_schedule(self):
        for document in self:
            document._compute_amortization_schedule()

    @api.multi
    def _compute_amortization_schedule(self):
        self.ensure_one()
        self.schedule_ids.unlink()
        amount = self._get_period_amount()
        obj_schedule = self.env[self._get_amortization_schedule_name()]
        pd_schedule = self._get_amortization_schedule()
        for period in range(0, self.period_number):
            if period == (self.period_number - 1):
                if self.amount != self.period_number * round(amount, 2):
                    amount = self.amount - (period * round(amount, 2))
            obj_schedule.create(
                {
                    "amortization_id": self.id,
                    "date": pd_schedule[period].strftime("%Y-%m-%d"),
                    "amount": amount,
                }
            )

    @api.multi
    def _get_amortization_schedule(self):
        self.ensure_one()
        return pd.date_range(
            start=self.date_start,
            periods=self.period_number,
            freq="M",
        ).to_pydatetime()

    @api.multi
    def _get_amortization_schedule_name(self):
        self.ensure_one()
        model_name = str(self._model)
        obj_field = self.env["ir.model.fields"]
        criteria = [
            ("model_id.model", "=", model_name),
            ("name", "=", "schedule_ids"),
        ]
        field = obj_field.search(criteria)[0]
        return field.relation

    @api.multi
    def _get_period_amount(self):
        self.ensure_one()
        return abs(np.pmt(0.0, self.period_number, self.amount))

    @api.model
    def create(self, values):
        _super = super(AccountAmortizationCommon, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write(
            {
                "name": sequence,
            }
        )
        return result

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(AccountAmortizationCommon, self)
        _super.unlink()

    @api.multi
    def validate_tier(self):
        _super = super(AccountAmortizationCommon, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_approve()

    @api.multi
    def restart_validation(self):
        _super = super(AccountAmortizationCommon, self)
        _super.restart_validation()
        for document in self:
            document.request_validation()
