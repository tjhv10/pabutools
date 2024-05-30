import unittest
from CSTV import Project, Doner, update_projects_support, reset_donations, calculate_total_initial_support, calculate_total_initial_support_doners, calculate_excess_support, select_max_excess_project, distribute_excess_support, cstv_budgeting
# from pabutools.rules.CSTV import Project, Doner, update_projects_support, reset_donations, calculate_total_initial_support, calculate_total_initial_support_doners, calculate_excess_support, select_max_excess_project, distribute_excess_support, cstv_budgeting
import random

class TestProject(unittest.TestCase):
    def setUp(self):
        self.project_A = Project("A", 37)
        self.project_B = Project("B", 30)
        self.project_C = Project("C", 40)

    def test_update_support(self):
        self.project_A.update_support([5, 10, 0, 0, 15])
        self.assertEqual(self.project_A.support, [5, 10, 0, 0, 15])  # Check if support list is correctly updated

class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.project_A = Project("A", 27)
        self.project_B = Project("B", 30)
        self.project_C = Project("C", 40)
        self.doner1 = Doner([5, 10, 5])
        self.doner2 = Doner([10, 10, 0])
        self.doner3 = Doner([0, 15, 5])
        self.doner4 = Doner([0, 0, 20])
        self.doner5 = Doner([15, 5, 0])
        self.projects = [self.project_A, self.project_B, self.project_C]
        self.doners = [self.doner1, self.doner2, self.doner3, self.doner4, self.doner5]

    def test_reset_donations(self):
        index = 0
        self.project_A.update_support([5, 10, 0, 0, 15])
        updated_projects = reset_donations(self.projects, index)
        self.assertEqual(updated_projects[index].support, [0, 0, 0, 0, 0])  # Ensure donations are reset to zero

    def test_calculate_total_initial_support(self):
        i = 0
        for project in self.projects:
            don = []
            for j in range(len(self.doners)):
                don.append(self.doners[j].get_donations()[i])
            project.update_support(don)
            i += 1
        self.assertEqual(calculate_total_initial_support(self.projects), 100)  # Verify total initial support calculation

    def test_distribute_excess_support(self):
        self.doner1.update_donations([5, 10, 5])
        self.doner2.update_donations([10, 10, 0])
        self.doner3.update_donations([0, 15, 5])
        self.doner4.update_donations([0, 0, 20])
        self.doner5.update_donations([15, 5, 0])
        self.projects = update_projects_support(self.projects, self.doners)
        max_excess_project, stam = select_max_excess_project(self.projects)
        gama = 0.5
        updated_projects = distribute_excess_support(self.projects, max_excess_project, self.doners, gama)
        expected_support_A = [7.5, 15.0, 0.0, 0, 22.5]  # Expected support distribution for Project A
        expected_support_B = [10, 10, 15, 0, 5]  # No change expected for max_excess_project (Project B)
        expected_support_C = [7.5, 0.0, 7.5, 20, 0.0]  # Expected support distribution for Project C
        self.assertEqual(updated_projects[0].support, expected_support_A)  # Verify updated support for Project A
        self.assertEqual(updated_projects[1].support, expected_support_B)  # Verify updated support for Project B
        self.assertEqual(updated_projects[2].support, expected_support_C)  # Verify updated support for Project C

    def test_calculate_excess_support(self):
        i = 0
        for project in self.projects:
            don = []
            for j in range(len(self.doners)):
                don.append(self.doners[j].get_donations()[i])
            project.update_support(don)
            i += 1
        self.assertEqual(calculate_excess_support(self.project_A), 3)  # Verify excess support calculation for Project A

    def test_select_max_excess_project(self):
        i = 0
        for project in self.projects:
            don = []
            for j in range(len(self.doners)):
                don.append(self.doners[j].get_donations()[i])
            project.update_support(don)
            i += 1
        max_excess_project, excess_support = select_max_excess_project(self.projects)
        self.assertEqual(max_excess_project.name, 'B')  # Verify correct project with maximum excess support
        self.assertEqual(excess_support, 10)  # Verify the amount of excess support

    def test_cstv_budgeting_with_zero_budget(self):
        """Test with zero budget across all doners."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            self.doner1.update_donations([0, 0, 0])
            self.doner2.update_donations([0, 0, 0])
            self.doner3.update_donations([0, 0, 0])
            self.doner4.update_donations([0, 0, 0])
            self.doner5.update_donations([0, 0, 0])
            self.projects = update_projects_support(self.projects, self.doners)
            selected_projects = cstv_budgeting(self.projects, self.doners, algo)
            self.assertEqual(selected_projects, [])  # Ensure no projects are selected when budget is zero

    def test_cstv_budgeting_with_budget_less_than_min_project_cost(self):
        """Test with total budget less than the minimum project cost."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            self.doner1.update_donations([5, 0, 0])
            self.doner2.update_donations([2, 2, 1])
            self.doner3.update_donations([4, 0, 1])
            self.doner4.update_donations([1, 0, 4])
            self.doner5.update_donations([1, 1, 3])
            self.projects = update_projects_support(self.projects, self.doners)
            selected_projects = cstv_budgeting(self.projects, self.doners, algo)
            self.assertEqual(selected_projects, [])  # Ensure no projects are selected when total budget is less than the minimum project cost

    def test_cstv_budgeting_with_budget_greater_than_max_total_needed_support(self):
        """Test with total budget greater than the sum of all project costs."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            self.doner1.update_donations([0, 0, 30])
            self.doner2.update_donations([30, 0, 0])
            self.doner3.update_donations([0, 15, 15])
            self.doner4.update_donations([25, 0, 5])
            self.doner5.update_donations([0, 30, 0])
            self.projects = update_projects_support(self.projects, self.doners)
            selected_projects = cstv_budgeting(self.projects, self.doners, algo)
            self.assertEqual(len(selected_projects), len(self.projects))  # Ensure all projects are selected when budget exceeds the total needed support
            self.assertEqual([project.name for project in selected_projects], ['A', 'B', 'C'])  # Verify the names of the selected projects

    def test_cstv_budgeting_with_budget_between_min_and_max(self):
        """Test with total budget between the minimum and maximum project costs."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            self.doner1.update_donations([5, 10, 5])
            self.doner2.update_donations([10, 10, 0])
            self.doner3.update_donations([0, 15, 5])
            self.doner4.update_donations([0, 0, 20])
            self.doner5.update_donations([15, 5, 0])
            self.projects = update_projects_support(self.projects, self.doners)
            selected_projects = cstv_budgeting(self.projects, self.doners, algo)
            self.assertEqual(len(selected_projects), 3)  # Ensure the number of selected projects is 3 when total budget is between the minimum and maximum costs
            self.assertEqual([project.name for project in selected_projects], ['B', 'A', 'C'])  # Verify the names of the selected projects

    def test_cstv_budgeting_with_budget_exactly_matching_required_support(self):
        """Test with total budget exactly matching the required support for all projects."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            self.doner1.update_donations([10, 20, 0])
            self.doner2.update_donations([20, 10, 0])
            self.doner3.update_donations([0, 0, 0])
            self.doner4.update_donations([0, 0, 25])
            self.doner5.update_donations([7, 0, 15])
            self.projects = update_projects_support(self.projects, self.doners)
            selected_projects = cstv_budgeting(self.projects, self.doners, algo)
            self.assertEqual(len(selected_projects), 3)  # Ensure all projects are selected when the total budget matches the required support exactly
            self.assertEqual([project.name for project in selected_projects], ['A', 'B', 'C'])  # Verify the names of the selected projects

class TestCSTVBudgetingNonLegalInput(unittest.TestCase):
    def test_cstv_budgeting_non_legal_input(self):
        """Test with non-legal input: a list of projects including a string instead of a Project object."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            projects = [Project("Project_1", 10), "Project_2"]
            doners = [Doner([10, 20, 30]), Doner([5, 5, 5])]
            with self.assertRaises(TypeError):
                cstv_budgeting(projects, doners, algo)  # Ensure TypeError is raised with non-legal input

class TestCSTVBudgetingLargeInput(unittest.TestCase):
    def test_cstv_budgeting_large_input(self):
        """Test with a large number of projects and doners."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            num_projects = 100
            num_doners = 100
            self.projects = [Project(f"Project_{i}", 50) for i in range(50)]
            self.projects += [Project(f"Project_{i+50}", 151) for i in range(50)]
            self.doners = [Doner([1] * num_projects) for _ in range(num_doners)]
            self.projects = update_projects_support(self.projects, self.doners)
            selected_projects = cstv_budgeting(self.projects, self.doners, algo)
            # Ensure the number of selected projects is equal to the total number of projects minus one
            self.assertEqual(len(selected_projects), len(self.projects) - 1)

class TestCSTVBudgetingLargeRandomInput(unittest.TestCase):
    def test_cstv_budgeting_large_random_input(self):
        """Test with a large number of projects and donors with random donations."""
        for algo in ["EwT", "EwTC", "MT", "MTC"]:
            self.projects = [Project(f"Project_{i}", random.randint(100, 1000)) for i in range(100)]
            self.doners = [Doner([random.randint(0, 5) for _ in range(len(self.projects))]) for _ in range(100)]
            self.projects = update_projects_support(self.projects, self.doners)
            positive_excess = sum(1 for p in self.projects if calculate_excess_support(p) >= 0)
            support = calculate_total_initial_support_doners(self.doners)
            selected_projects = cstv_budgeting(self.projects, self.doners, algo)
            total_cost = sum(project.get_cost() for project in selected_projects)
            # Ensure the number of selected projects does not exceed the total number of projects
            self.assertGreaterEqual(100, len(selected_projects))
            # Ensure the number of selected projects is at least the number of projects with non-negative excess support
            self.assertGreaterEqual(len(selected_projects), positive_excess)
            # Ensure the total initial support from donors is at least the total cost of the selected projects
            self.assertGreaterEqual(support, total_cost)

if __name__ == '__main__':
    unittest.main()
