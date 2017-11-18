# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Disposition of Variance",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "account_accountant",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/account_journal_views.xml",
        "views/account_variance_computation_views.xml",
    ],
}
