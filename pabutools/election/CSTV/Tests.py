import unittest
from algorithm import Project, Doner, update_projects_support,find_project_index, get_project_names, reset_donations, calculate_total_initial_support,calculate_total_initial_support_doners, calculate_excess_support, select_max_excess_project, distribute_excess_support, cstv_budgeting
import random
class TestProject(unittest.TestCase):
    def setUp(self):
        self.project_A = Project("A", 37)
        self.project_B = Project("B", 30)
        self.project_C = Project("C", 40)
        self.doner1 = Doner([5, 10, 5])
        self.doner2 = Doner([10, 10, 0])
        self.doner3 = Doner([0, 15, 5])
        self.doner4 = Doner([0, 0, 20])
        self.doner5 = Doner([15, 5, 0])
        
    def test_add_support(self):
        self.project_A.update_support([5, 10, 0, 0, 15])
        self.assertEqual(self.project_A.support, [5, 10, 0, 0, 15])

    def test_get_name(self):
        self.assertEqual(self.project_A.get_name(), "A")

    def test_get_cost(self):
        self.assertEqual(self.project_A.get_cost(), 37)

    def test_find_project_index(self):
        projects = [self.project_A, self.project_B, self.project_C]
        self.assertEqual(find_project_index(projects, "B"), 1)
        self.assertEqual(find_project_index(projects, "D"), -1)

    def test_get_project_names(self):
        projects = [self.project_A, self.project_B, self.project_C]
        self.assertEqual(get_project_names(projects), ['A', 'B', 'C'])

class TestDoner(unittest.TestCase):
    def setUp(self):
        self.doner1 = Doner([5, 10, 5])
        self.doner2 = Doner([10, 10, 0])
        self.doner3 = Doner([0, 15, 5])
        self.doner4 = Doner([0, 0, 20])
        self.doner5 = Doner([15, 5, 0])

    def test_get_donations(self):
        self.assertEqual(self.doner1.get_donations(), [5, 10, 5])


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
        
        self.assertEqual(updated_projects[index].support, [0, 0, 0, 0, 0])

    def test_calculate_total_initial_support(self):
        i =0
        for project in self.projects:
            don =[]
            for j in range(0,len(self.doners)):
                don.append(self.doners[j].get_donations()[i])
            project.update_support(don)
            i+=1
        self.assertEqual(calculate_total_initial_support(self.projects), 100)



    def test_distribute_excess_support(self):
        self.doner1.update_donations([5,10,5])
        self.doner2.update_donations([10,10,0])
        self.doner3.update_donations([0,15,5])
        self.doner4.update_donations([0,0,20])
        self.doner5.update_donations([15,5,0])
        self.projects = update_projects_support(self.projects,self.doners)
        max_excess_project,stam = select_max_excess_project(self.projects)
        gama = 0.5
        updated_projects = distribute_excess_support(self.projects, max_excess_project, self.doners, gama)
        expected_support_A = [7.5, 15.0, 0.0, 0, 22.5]  # No change expected for max_excess_project
        expected_support_B = [10, 10, 15, 0, 5]
        expected_support_C = [7.5, 0.0, 7.5, 20, 0.0]
        self.assertEqual(updated_projects[0].support, expected_support_A)
        self.assertEqual(updated_projects[1].support, expected_support_B)
        self.assertEqual(updated_projects[2].support, expected_support_C)

    def test_calculate_excess_support(self):
        i =0
        for project in self.projects:
            don =[]
            for j in range(0,len(self.doners)):
                don.append(self.doners[j].get_donations()[i])
            project.update_support(don)
            i+=1
        self.assertEqual(calculate_excess_support(self.project_A), 3)

    def test_select_max_excess_project(self):
        i =0
        for project in self.projects:
            don =[]
            for j in range(0,len(self.doners)):
                don.append(self.doners[j].get_donations()[i])
            project.update_support(don)
            i+=1
        max_excess_project, excess_support = select_max_excess_project(self.projects)
        self.assertEqual(max_excess_project.name, 'B')
        self.assertEqual(excess_support, 10)

    def test_cstv_budgeting_with_zero_budget(self):
        self.doner1.update_donations([0,0,0])
        self.doner2.update_donations([0,0,0])
        self.doner3.update_donations([0,0,0])
        self.doner4.update_donations([0,0,0])
        self.doner5.update_donations([0,0,0])
        self.projects = update_projects_support(self.projects,self.doners)
        selected_projects = cstv_budgeting(self.projects, self.doners)
        self.assertEqual(selected_projects, [])

    def test_cstv_budgeting_with_budget_less_than_min_project_cost(self):
        self.doner1.update_donations([5,0,0])
        self.doner2.update_donations([2,2,1])
        self.doner3.update_donations([4,0,1])
        self.doner4.update_donations([1,0,4])
        self.doner5.update_donations([1,1,3])
        self.projects = update_projects_support(self.projects,self.doners)
        selected_projects = cstv_budgeting(self.projects, self.doners)
        self.assertEqual(selected_projects, [])

    def test_cstv_budgeting_with_budget_greater_than_max_total_needed_support(self):
        self.doner1.update_donations([0,0,30])
        self.doner2.update_donations([30,0,0])
        self.doner3.update_donations([0,15,15])
        self.doner4.update_donations([25,0,5])
        self.doner5.update_donations([0,30,0])
        self.projects = update_projects_support(self.projects,self.doners)
        selected_projects = cstv_budgeting(self.projects, self.doners)
        self.assertEqual(len(selected_projects), len(self.projects))
        self.assertEqual([project.name for project in selected_projects], ['A', 'B', 'C'])

    def test_cstv_budgeting_with_budget_between_min_and_max(self):
        self.doner1.update_donations([5,10,5])
        self.doner2.update_donations([10,10,0])
        self.doner3.update_donations([0,15,5])
        self.doner4.update_donations([0,0,20])
        self.doner5.update_donations([15,5,0])
        self.projects = update_projects_support(self.projects,self.doners)
        selected_projects = cstv_budgeting(self.projects, self.doners)
        self.assertEqual(len(selected_projects), 2)
        self.assertEqual([project.name for project in selected_projects], ['B', 'A'])

    def test_cstv_budgeting_with_budget_exactly_matching_requierd_support(self):
        self.doner1.update_donations([10,20,0])
        self.doner2.update_donations([20,10,0])
        self.doner3.update_donations([0,0,0])
        self.doner4.update_donations([0,0,25])
        self.doner5.update_donations([7,0,15])
        self.projects = update_projects_support(self.projects,self.doners)
        selected_projects = cstv_budgeting(self.projects, self.doners)
        self.assertEqual(len(selected_projects), 3)
        self.assertEqual([project.name for project in selected_projects], ['A', 'B', 'C'])

class TestCSTVBudgetingNonLegalInput(unittest.TestCase):
    def test_cstv_budgeting_non_legal_input(self):
        # Creating a list of projects with one of them being a string instead of a Project object
        projects = [Project("Project_1", 10), "Project_2"]
        
        # Creating a list of doners
        doners = [Doner([10, 20, 30]), Doner([5, 5, 5])]
        
        # Running the budgeting algorithm with non-legal input
        with self.assertRaises(TypeError):
            cstv_budgeting(projects, doners)

class TestCSTVBudgetingLargeInput(unittest.TestCase):
    def test_cstv_budgeting_large_input(self):
        # Creating a large number of projects and doners
        num_projects = 100
        num_doners = 100
        self.projects = [Project(f"Project_{i}", 50) for i in range(50)]
        self.projects += [Project(f"Project_{i+50}", 151) for i in range(50)]
        
        self.doners = [Doner([1] * num_projects) for _ in range(num_doners)]
        self.projects = update_projects_support(self.projects,self.doners)

        # Running the budgeting algorithm with a large input
        selected_projects = cstv_budgeting(self.projects, self.doners)
        self.assertEqual(len(selected_projects), len(self.projects)-1)


class TestCSTVBudgetingLargeRandomInput(unittest.TestCase):
    def test_cstv_budgeting_large_random_input(self):
        # Creating 100 projects with random costs between 10 and 100
        self.projects = [Project(f"Project_{i}", random.randint(100, 1000)) for i in range(100)]
        # Creating 100 doners with random donations between 0 and 50 for each project
        self.doners = [Doner([random.randint(0, 5) for _ in range(len(self.projects))]) for _ in range(100)]
        # Assigning support for each project from the values of the doners
        self.projects = update_projects_support(self.projects,self.doners)
        positiveExcess = 0
        for p in self.projects:
           if calculate_excess_support(p)>=0:
                positiveExcess+=1

        support = calculate_total_initial_support_doners(self.doners)
        selected_projects = cstv_budgeting(self.projects, self.doners)
        sum = 0
        for project in selected_projects:
            sum+= project.get_cost()
        self.assertGreaterEqual(100,len(selected_projects))
        self.assertGreaterEqual(len(selected_projects),positiveExcess)
        self.assertGreaterEqual(support,sum)

if __name__ == '__main__':
    unittest.main()
