# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    avalaible_for_variance_computation = fields.Boolean(
        string="Avalaible for Variance Computation",
    )
