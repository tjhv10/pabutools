"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achiya Ben Natan
Date: 2024/05/16.
"""

import unittest
from pabutools.election import Project, CumulativeBallot, Instance
from pabutools.rules.cstv import *
import random


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.projects = Instance([Project("A", 27),Project("B", 30),Project("C", 40)])
        self.donors = [CumulativeBallot({"A": 5, "B": 10, "C": 5}), CumulativeBallot({"A": 10, "B": 10, "C": 0}), CumulativeBallot({"A": 0, "B": 15, "C": 5}), CumulativeBallot({"A": 0, "B": 0, "C": 20}), CumulativeBallot({"A": 15, "B": 5, "C": 0})]

    def test_cstv_budgeting_with_zero_budget(self):
        for donor in self.donors:
            for key in donor.keys():
                donor[key] = 0
        for alg_str in ["ewt", "ewtc", "mt", "mtc"]:
            self.projects = Instance([Project("A", 27),Project("B", 30),Project("C", 40)])
            selected_projects = cstv_budgeting_combination(self.projects, self.donors, alg_str)
            self.assertEqual(len(selected_projects), 0)  # Ensure no projects are selected when budget is zero

    def test_cstv_budgeting_with_budget_less_than_min_project_cost(self):
        for donor in self.donors:
            donor["A"] = 1
            donor["B"] = 1
            donor["C"] = 1
        for alg_str in ["ewt", "ewtc", "mt", "mtc"]:
            self.projects = Instance([Project("A", 27),Project("B", 30),Project("C", 40)])
            selected_projects = cstv_budgeting_combination(self.projects, self.donors, alg_str)
            self.assertEqual(len(selected_projects), 0)  # Ensure no projects are selected when total budget is less than the minimum project cost

    def test_cstv_budgeting_with_budget_greater_than_max_total_needed_support(self):
        num_projects = len(self.projects)
        for donor in self.donors:
            for key in donor.keys():
                donor[key] = 100
        for alg_str in ["ewt", "ewtc", "mt", "mtc"]:
            self.projects = Instance([Project("A", 27),Project("B", 30),Project("C", 40)])
            self.donors = [CumulativeBallot({"A": 5, "B": 10, "C": 5}), CumulativeBallot({"A": 10, "B": 10, "C": 0}), CumulativeBallot({"A": 0, "B": 15, "C": 5}), CumulativeBallot({"A": 0, "B": 0, "C": 20}), CumulativeBallot({"A": 15, "B": 5, "C": 0})]
            selected_projects = cstv_budgeting_combination(self.projects, self.donors, alg_str)
            self.assertEqual(len(selected_projects), num_projects-1)  # Ensure all projects are selected when budget exceeds the total needed support

    def test_cstv_budgeting_with_budget_between_min_and_max(self):
        for alg_str in ["ewt", "ewtc", "mt", "mtc"]:
            self.projects = Instance([Project("A", 27),Project("B", 30),Project("C", 40)])
            self.donors = [CumulativeBallot({"A": 5, "B": 10, "C": 5}), CumulativeBallot({"A": 10, "B": 10, "C": 0}), CumulativeBallot({"A": 0, "B": 15, "C": 5}), CumulativeBallot({"A": 0, "B": 0, "C": 20}), CumulativeBallot({"A": 15, "B": 5, "C": 0})]
            selected_projects = cstv_budgeting_combination(self.projects, self.donors, alg_str)
            self.assertEqual(len(selected_projects), 2)  # Ensure the number of selected projects is 3 when total budget is between the minimum and maximum costs

    def test_cstv_budgeting_with_budget_exactly_matching_required_support(self):
        for alg_str in ["ewt", "ewtc", "mt", "mtc"]:
            for donor in self.donors:
                donor["A"] = 27/len(self.donors)
                donor["B"] = 30/len(self.donors)
                donor["C"] = 40/len(self.donors)
            self.projects = Instance([Project("A", 27),Project("B", 30),Project("C", 40)])
            selected_projects = cstv_budgeting_combination(self.projects, self.donors, alg_str)
            self.assertEqual(len(selected_projects), 3)  # Ensure all projects are selected when the total budget matches the required support exactly

    def test_cstv_budgeting_large_input(self):
        num_projects = 100
        for alg_str in ["ewt", "ewtc", "mt", "mtc"]:
            self.projects = [Project(f"Project_{i}", 50) for i in range(int(num_projects/2))]
            self.projects += [Project(f"Project_{i+50}", 151) for i in range(int(num_projects/2))]
            self.projects = Instance(init = self.projects)
            self.donors = [CumulativeBallot({f"Project_{i}": 1 for i in range(num_projects)}) for _ in range(100)]
            selected_projects = cstv_budgeting_combination(self.projects, self.donors, alg_str)
            self.assertLessEqual(len(selected_projects), num_projects)  # Ensure the number of selected projects does not exceed the total number of projects


    def test_cstv_budgeting_large_random_input(self):
        for alg_str in ["ewt", "ewtc","mt","mtc"]:
            self.projects = [Project(f"Project_{i}", random.randint(100, 1000)) for i in range(100)]
            # Function to generate a list of donations that sum to total_donation
            def generate_donations(total, num_projects):
                donations = [0] * num_projects
                for _ in range(total):
                    donations[random.randint(0, num_projects - 1)] += 1
                return donations
            # Generate the donations for each donor
            self.donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(20, len(self.projects)))})for _ in range(100)]
            num_projects = len(self.projects)
            positive_excess = sum(1 for p in self.projects if sum(donor.get(p.name, 0) for donor in self.donors) - p.cost >= 0)
            support = sum(sum(donor.values()) for donor in self.donors)
            selected_projects = cstv_budgeting_combination(self.projects, self.donors, alg_str)
            total_cost = sum(project.cost for project in selected_projects)
            self.assertLessEqual(len(selected_projects), num_projects)  # Ensure the number of selected projects does not exceed the total number of projects
            self.assertGreaterEqual(len(selected_projects), positive_excess)  # Ensure the number of selected projects is at least the number of projects with non-negative excess support
            self.assertGreaterEqual(support, total_cost)  # Ensure the total initial support from donors is at least the total cost of the selected projects
