# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountAmortizationTypeAccountMapping(models.Model):
    _name = "account.amortization_type_account_mapping"
    _description = "Amortization Type Account Mapping"

    type_id = fields.Many2one(
        string="Type",
        comodel_name="account.amortization_type",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    contra_account_id = fields.Many2one(
        string="Contra Account",
        comodel_name="account.account",
    )
