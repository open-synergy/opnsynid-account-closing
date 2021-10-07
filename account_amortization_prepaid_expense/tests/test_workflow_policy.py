# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from ddt import ddt, file_data

from .base import BaseCase


@ddt
class TestWorkflowPolicy(BaseCase):
    def _update_groups(self, user, groups):
        user.write({"groups_id": [(6, 0, [])]})
        group_ids = []
        for group_name in groups:
            group = getattr(self, group_name)
            group_ids.append(group.id)
        user.write({"groups_id": [(6, 0, group_ids)]})

    @file_data("scenario_workflow.yaml")
    def test_prepaid_expense_amortization_workflow_policy(self, attribute, policies):
        user = getattr(self, attribute["user"])
        self._update_groups(user, attribute["groups"])
        values = {
            "type_id": self.type_amortization.id,
        }
        if attribute["super_user"]:
            amortization = self.obj_amortization.new(values)
        else:
            amortization = self.obj_amortization.sudo(user).new(values)
        for policy in policies:
            field_to_check = getattr(amortization, policy["name"])
            correct_value = policy["status"]
            self.assertEqual(field_to_check, correct_value)
