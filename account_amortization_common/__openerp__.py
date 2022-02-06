# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Common Amortization Feature",
    "version": "8.0.2.3.0",
    "category": "Accounting",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "account_accountant",
        "base_sequence_configurator",
        "base_workflow_policy",
        "base_cancel_reason",
        "base_print_policy",
        "base_multiple_approval",
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
        "wizards/wizard_schedule_amortization_views.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
