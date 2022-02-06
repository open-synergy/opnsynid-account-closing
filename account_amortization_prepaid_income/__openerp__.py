# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Prepaid Income Amortization",
    "version": "8.0.1.1.0",
    "category": "Accounting",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "account_amortization_common",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/amortization_type_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "data/base_cancel_reason_configurator_data.xml",
        "data/ir_cron.xml",
        "views/account_prepaid_income_amortization_views.xml",
    ],
    "demo": [
        "demo/account_journal_demo.xml",
        "demo/tier_definition_demo.xml",
        "demo/account_account_demo.xml",
        "demo/account_amortization_type_account_mapping_demo.xml",
    ],
}
