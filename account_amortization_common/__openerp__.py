# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Common Amortization Feature",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "account_accountant",
        "base_sequence_configurator",
        "base_workflow_policy",
        "base_cancel_reason",
        "base_print_policy",
    ],
    "external_dependencies": {
        "python": [
            "pandas",
            "numpy",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "menu.xml",
        "views/account_amortization_type_views.xml",
        "views/account_amortization_common_views.xml",
    ],
}
