# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountAmortizationType(models.Model):
    _name = "account.amortization_type"
    _description = "Amortization Type"

    name = fields.Char(
        string="Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    direction = fields.Selection(
        string="Direction",
        selection=[
            ("dr", "Debit"),
            ("cr", "Credit"),
        ],
        default="dr",
        required=True,
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
    )
    journal_id = fields.Many2one(
        string="Default Journal",
        comodel_name="account.journal",
    )
    account_mapping_ids = fields.One2many(
        string="Account Mapping",
        comodel_name="account.amortization_type_account_mapping",
        inverse_name="type_id",
    )
    amortization_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Amortization",
        comodel_name="res.groups",
        relation="rel_amortization_type_confirm_amortization",
        column1="amortization_id",
        column2="group_id",
    )
    amortization_restart_validation_grp_ids = fields.Many2many(
        string="Allow To Restart Validation Amortization",
        comodel_name="res.groups",
        relation="rel_amortization_type_restart_validation_amortization",
        column1="amortization_id",
        column2="group_id",
    )
    amortization_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Amortization",
        comodel_name="res.groups",
        relation="rel_amortization_type_cancel_amortization",
        column1="amortization_id",
        column2="group_id",
    )
    amortization_restart_grp_ids = fields.Many2many(
        string="Allow To Cancel Amortization",
        comodel_name="res.groups",
        relation="rel_amortization_type_restart_amortization",
        column1="amortization_id",
        column2="group_id",
    )
    note = fields.Text(
        string="Note",
    )
