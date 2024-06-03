import unittest
from pabutools.election import Project, CumulativeBallot
from pabutools.rules.CSTV import *
import random

class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.project_A = Project("A", 27)
        self.project_B = Project("B", 30)
        self.project_C = Project("C", 40)
        self.doner1 = CumulativeBallot({"A": 5, "B": 10, "C": 5})
        self.doner2 = CumulativeBallot({"A": 10, "B": 10, "C": 0})
        self.doner3 = CumulativeBallot({"A": 0, "B": 15, "C": 5})
        self.doner4 = CumulativeBallot({"A": 0, "B": 0, "C": 20})
        self.doner5 = CumulativeBallot({"A": 15, "B": 5, "C": 0})
        self.projects = [self.project_A, self.project_B, self.project_C]
        self.doners = [self.doner1, self.doner2, self.doner3, self.doner4, self.doner5]

    def test_reset_donations(self):
        index = "A"
        updated_doners = reset_donations(self.doners, index)
        for doner in updated_doners:
            self.assertEqual(doner.get(index), 0)  # Ensure donations are reset to zero

    def test_calculate_total_initial_support(self):
        total_initial_support = calculate_total_initial_support(self.doners, self.projects)
        self.assertEqual(total_initial_support, 100)  # Verify total initial support calculation

    def test_distribute_excess_support(self):
        max_excess_project = self.project_B
        gama = 0.5
        excess_redistribution_procedure(self.projects, max_excess_project, self.doners, gama, ["A", "B", "C"])
        self.assertAlmostEqual(sum(doner["B"] for doner in self.doners), 0)  # Ensure B donations are reset

    def test_calculate_excess_support(self):
        excess_support = calculate_excess_support(self.doners, self.project_A)

        self.assertEqual(excess_support, 3)  # Verify excess support calculation for Project A

    def test_select_project_GE(self):
        selected_project = select_project_GE(self.doners, self.projects)
        self.assertEqual(selected_project.name, 'B')  # Verify correct project with maximum excess support

    def test_cstv_budgeting_with_zero_budget(self):
        for doner in self.doners:
            for key in doner.keys():
                doner[key] = 0
        selected_projects = cstv_budgeting(self.doners, self.projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
        self.assertEqual(selected_projects, [])  # Ensure no projects are selected when budget is zero

    def test_cstv_budgeting_with_budget_less_than_min_project_cost(self):
        for doner in self.doners:
            doner["A"] = 1
            doner["B"] = 1
            doner["C"] = 1
        selected_projects = cstv_budgeting(self.doners, self.projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
        self.assertEqual(selected_projects, [])  # Ensure no projects are selected when total budget is less than the minimum project cost

    def test_cstv_budgeting_with_budget_greater_than_max_total_needed_support(self):
        num_projects = len(self.projects)
        for doner in self.doners:
            for key in doner.keys():
                doner[key] = 100
        selected_projects = cstv_budgeting(self.doners, self.projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
        self.assertEqual(len(selected_projects), num_projects)  # Ensure all projects are selected when budget exceeds the total needed support
        self.assertEqual([project.name for project in selected_projects], ['A', 'B', 'C'])  # Verify the names of the selected projects

    def test_cstv_budgeting_with_budget_between_min_and_max(self):
        selected_projects = cstv_budgeting(self.doners, self.projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
        self.assertEqual(len(selected_projects), 2)  # Ensure the number of selected projects is 2 when total budget is between the minimum and maximum costs
        self.assertEqual([project.name for project in selected_projects], ['B', 'A'])  # Verify the names of the selected projects

    def test_cstv_budgeting_with_budget_exactly_matching_required_support(self):
        for doner in self.doners:
            doner["A"] = 27
            doner["B"] = 30
            doner["C"] = 40
        selected_projects = cstv_budgeting(self.doners, self.projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
        self.assertEqual(len(selected_projects), 3)  # Ensure all projects are selected when the total budget matches the required support exactly
        self.assertEqual([project.name for project in selected_projects], ['A', 'B', 'C'])  # Verify the names of the selected projects

    def test_cstv_budgeting_large_input(self):
        num_projects = 100
        num_doners = 100
        self.projects = [Project(f"Project_{i}", 50) for i in range(50)]
        self.projects += [Project(f"Project_{i+50}", 151) for i in range(50)]
        self.doners = [CumulativeBallot({f"Project_{i}": 1 for i in range(num_projects)}) for _ in range(num_doners)]
        selected_projects = cstv_budgeting(self.doners, self.projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
        self.assertLessEqual(len(selected_projects), num_projects-1)  # Ensure the number of selected projects does not exceed the total number of projects


    def test_cstv_budgeting_large_random_input(self):
        self.projects = [Project(f"Project_{i}", random.randint(100, 1000)) for i in range(100)]
        total_donation = 20

        # Function to generate a list of donations that sum to total_donation
        def generate_donations(total, num_projects):
            donations = [0] * num_projects
            for _ in range(total):
                donations[random.randint(0, num_projects - 1)] += 1
            return donations

        # Generate the donations for each donor
        self.doners = [
            CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(total_donation, len(self.projects)))})
            for _ in range(100)
        ]
        num_projects = len(self.projects)
        positive_excess = sum(1 for p in self.projects if calculate_excess_support(self.doners, p) >= 0)
        support = calculate_total_initial_support_doners(self.doners)
        selected_projects = cstv_budgeting(self.doners, self.projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
        
        total_cost = sum(project.cost for project in selected_projects)
        self.assertLessEqual(len(selected_projects), num_projects)  # Ensure the number of selected projects does not exceed the total number of projects
        self.assertGreaterEqual(len(selected_projects), positive_excess)  # Ensure the number of selected projects is at least the number of projects with non-negative excess support
        self.assertGreaterEqual(support, total_cost)  # Ensure the total initial support from donors is at least the total cost of the selected projects

if __name__ == '__main__':
    unittest.main()
