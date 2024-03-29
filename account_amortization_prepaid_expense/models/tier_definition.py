# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import api, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):  # pragma: no cover
        res = super(TierDefinition, self)._get_tier_validation_model_names()
        res.append("account.prepaid_expense_amortization")
        return res
