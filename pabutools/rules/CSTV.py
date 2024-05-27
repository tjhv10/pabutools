
"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achia Ben Natan
Date: 2024/05/16.
"""
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

class Project:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.support = []

    def update_support(self, support):
        self.support = support

    def get_name(self):
        return self.name

    def get_cost(self):
        return self.cost

    def __str__(self):
        supporter_strings = ", ".join(str(s) for s in self.support)
        return f"Project: {self.name}, Cost: {self.cost}, Initial support: [{supporter_strings} sum:{sum(self.support)}]"

class Doner:
    def __init__(self, donations):
        self.donations = donations

    def get_donations(self):
        return self.donations

    def update_donations(self, donation):
        self.donations = donation

def find_project_index(projects, project_name):
    return next((i for i, project in enumerate(projects) if project.get_name() == project_name), -1)

def get_project_names(projects):
    return [project.name for project in projects]

def reset_donations(projects, index):
    for project in projects:
        if project == projects[index]:
            project.support = [0 for supporter in project.support]
    return projects

def calculate_total_initial_support(projects):
    return sum(sum(project.support) for project in projects)

def calculate_total_initial_support_doners(doners):
    return sum(sum(doner.get_donations()) for doner in doners)

def calculate_excess_support(project):
    return sum(project.support) - project.cost

def select_max_excess_project(projects):
    excess_support = {project: calculate_excess_support(project) for project in projects}
    max_excess_project = max(excess_support, key=excess_support.get)
    return max_excess_project, excess_support[max_excess_project]

def distribute_excess_support(projects, max_excess_project, doners, gama):
    max_index = find_project_index(projects, max_excess_project.get_name())
    for project in projects:
        if project.get_name() != max_excess_project.get_name():
            for j, supporter in enumerate(project.support):
                if doners[j].get_donations()[max_index] != 0:
                    project.support[j] += supporter * (1 - gama)
    return projects

def update_projects_support(projects, doners):
    for i, project in enumerate(projects):
        don = []
        for doner in doners:
            don.append(doner.get_donations()[i])
        project.update_support(don)
    return projects

def gsc_score(project, L, n):
    cost = project.get_cost()
    support = sum(project.support)
    return (1 / cost) * (support * (L / n))

def select_gsc_project(projects, L, n):
    gsc_scores = {project: gsc_score(project, L, n) for project in projects}
    max_gsc_project = max(gsc_scores, key=gsc_scores.get)
    return max_gsc_project
def update_donors_with_project_support(projects, doners):
    for i, doner in enumerate(doners):
        updated_donations = [project.support[i] for project in projects]
        doner.update_donations(updated_donations)
    return doners

def cstv_budgeting(projects, doners, algorithm_selection_string):
    if not all(isinstance(project, Project) for project in projects):
        raise TypeError("All elements in the 'projects' list must be instances of the 'Project' class.")
    if not all(isinstance(doner, Doner) for doner in doners):
        raise TypeError("All elements in the 'doners' list must be instances of the 'Doner' class.")

    selected_projects = []
    budget = calculate_total_initial_support_doners(doners)
    L = budget
    if algorithm_selection_string == "EwTC":
        while True:
            # Implementation of GSC with Minimal-Transfers (MT)
            # Select project eligible for funding by transfers based on the highest ratio of support to cost
            eligible_projects = [project for project in projects if (sum(project.support) / project.cost) >= 1]
            if not eligible_projects:
                #TODO put here EwT
                break
            selected_project = max(eligible_projects, key=lambda x: sum(x.support) / x.cost)
            excess_support = calculate_excess_support(selected_project)
            if excess_support >= 0:
                selected_projects.append(selected_project)
                gama = selected_project.get_cost() / (excess_support + selected_project.get_cost())
                projects = distribute_excess_support(projects, selected_project, doners, gama)
                projects.remove(selected_project)
                budget -= selected_project.cost
                continue
            # Calculate proportional transfers to make the selected project eligible
            ratio = sum(selected_project.support) / selected_project.cost
            for i, voter_supports in enumerate(selected_project.support):
                if voter_supports > 0:
                    transfer_amount = min(voter_supports, ratio)
                    for j, project in enumerate(projects):
                        if i < len(project.support):
                            project.support[i] -= transfer_amount * (project.cost / L)
            projects = [project for project in projects if project.cost <= budget]
            if not projects:
                break
    else:
        while True:

            # Implementation of GE with Elimination-with-Transfers (EwT)
            max_excess_project, excess = select_max_excess_project(projects)
            if excess <= 0:
                break
            selected_projects.append(max_excess_project)
            gama = max_excess_project.get_cost() / (excess + max_excess_project.get_cost())
            projects = distribute_excess_support(projects, max_excess_project, doners, gama)
            k = find_project_index(projects, max_excess_project.get_name())
            projects = reset_donations(projects, k)
            budget -= max_excess_project.cost
            projects = [project for project in projects if project.cost <= budget]
            if not projects:
                break
    return selected_projects



def main():
    # Example projects and doners for testing
    project_A = Project("Project A", 35)
    project_B = Project("Project B", 30)
    project_C = Project("Project C", 35)
    
    doner1 = Doner([5, 10, 5])
    doner2 = Doner([10, 10, 0])
    doner3 = Doner([0, 15, 5])
    doner4 = Doner([0, 0, 20])
    doner5 = Doner([15, 5, 0])
    
    projects = [project_A, project_B, project_C]
    doners = [doner1, doner2, doner3, doner4, doner5]
    projects = update_projects_support(projects,doners)
    # Run the participatory budgeting process
    selected_projects = cstv_budgeting(projects, doners,"GE")    
    # Print the selected projects
    for project in selected_projects:
        print(f"Selected Project: {project.get_name()}, Cost: {project.get_cost()}")
if __name__ == "__main__":
    main()
    import doctest
    doctest.testmod()
