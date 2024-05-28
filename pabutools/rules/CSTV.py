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


def get_project_names(projects):
    return [project.name for project in projects]

def reset_donations(doners, index):
    """
    Reset the donations of a donor at the given index to 0.

    Parameters:
    - doners: list of Doner instances
    - index: the index of the donor to reset donations for

    Returns:
    - updated_doners: list of Doner instances with updated donations
    """
    for doner in doners:
        doner.donations[index] = 0
    return doners

def calculate_total_initial_support(projects):
    return sum(sum(project.support) for project in projects)

def calculate_total_initial_support_doners(doners):
    return sum(sum(doner.get_donations()) for doner in doners)

def calculate_excess_support(project):
    return sum(project.support) - project.cost

def select_max_excess_project(projects):
    excess_support = {project: calculate_excess_support(project) for project in projects}
    max_excess_project = max(excess_support, key=excess_support.get)
    return max_excess_project

def distribute_excess_support(projects, max_excess_project, doners, gama, listNames):
    max_index = find_project_index(listNames, max_excess_project.get_name())
    for doner in doners:
        toDistribute = doner.get_donations()[max_index] * (1 - gama)
        doner.get_donations()[max_index] = 0
        total = sum(doner.get_donations())
        for i, donetion in enumerate(doner.get_donations()):
            if i != max_index:
                if total != 0:
                    part = donetion / total
                    doner.get_donations()[i] = donetion + toDistribute * part
    return projects

def update_projects_support(projects, doners):
    indexes_to_go_over = []
    for i, doner in enumerate(doners):
        if sum(doner.get_donations()) > 0:
            indexes_to_go_over.append(i)
    if len(indexes_to_go_over) == 0:
        return projects
    index = 0
    for i, project in enumerate(projects):
        don = []
        for doner in doners:
            don.append(doner.get_donations()[indexes_to_go_over[index]])
        project.update_support(don)
        index += 1
    return projects

def get_project_names(projects):
    """
    Get the names of projects from a list of Project instances.

    Parameters:
    - projects: list of Project instances

    Returns:
    - project_names: list of project names
    """
    return [project.get_name() for project in projects]

def gsc_score(project, L, n):
    cost = project.get_cost()
    support = sum(project.support)
    return (1 / cost) * (support * (L / n))

def select_gsc_project(projects, L, n):
    gsc_scores = {project: gsc_score(project, L, n) for project in projects}
    max_gsc_project = max(gsc_scores, key=gsc_scores.get)
    return max_gsc_project

def update_donors_with_project_support(projects, doners):
    """
    Update the donations of donors based on the support for each project.

    Parameters:
    - projects: list of Project instances
    - doners: list of Doner instances

    Returns:
    - updated_doners: list of Doner instances with updated donations
    """
    for i, doner in enumerate(doners):
        updated_donations = [project.support[i] for project in projects]
        doner.update_donations(updated_donations)
    return doners

def distribute_project_support(projects, eliminated_project, doners, listNames):
    max_index = find_project_index(listNames, eliminated_project.get_name())
    for doner in doners:
        toDistribute = doner.get_donations()[max_index]
        total = sum(doner.get_donations())
        if total == 0:
            continue
        for i, donetion in enumerate(doner.get_donations()):
            if i != max_index:
                part = donetion / total
                doner.get_donations()[i] = donetion + toDistribute * part
    doners = reset_donations(doners, max_index)
    return update_projects_support(projects, doners)

def find_project_index(listNames, project_name):
    return next((i for i, project in enumerate(listNames) if project == project_name), -1)

def elimination_with_transfers(projects, doners, listNames, eliminated_projects):
    """
    Perform the Elimination-with-Transfers (EwT) algorithm on a list of projects with donor support.

    Parameters:
    - projects: list of Project instances
    - doners: list of Doner instances
    - eliminated_projects: list of Project instances that have been eliminated

    Returns:
    - selected_projects: list of Project instances that are selected for funding
    """
    if len(projects) < 2:
        return projects
    
    while projects:
        # Select the project with the minimum excess support
        min_project = min(projects, key=lambda p: calculate_excess_support(p))

        # Calculate excess support of the selected project
        excess = calculate_excess_support(min_project)

        if excess < 0:
            # Eliminate the project with minimum excess support
            projects = distribute_project_support(projects, min_project, doners, listNames)
            projects = update_projects_support(projects, doners)
            projects.remove(min_project)
            eliminated_projects.append(min_project)
            break

    return projects

def reverse_eliminations(selected_projects, eliminated_projects, budget):
    """
    Perform the Reverse Eliminations (RE) procedure.

    Parameters:
    - selected_projects: list of Project instances that are selected for funding
    - eliminated_projects: list of Project instances that have been eliminated
    - budget: remaining budget

    Returns:
    - selected_projects: updated list of Project instances that are selected for funding
    """
    for project in reversed(eliminated_projects):
        if project.get_cost() <= budget:
            selected_projects.append(project)
            budget -= project.get_cost()
    return selected_projects

def cstv_budgeting(projects, doners, algorithm_selection_string):
    if not all(isinstance(project, Project) for project in projects):
        raise TypeError("All elements in the 'projects' list must be instances of the 'Project' class.")
    if not all(isinstance(doner, Doner) for doner in doners):
        raise TypeError("All elements in the 'doners' list must be instances of the 'Doner' class.")

    selected_projects = []
    eliminated_projects = []
    budget = calculate_total_initial_support_doners(doners)
    listNames = get_project_names(projects)
    if algorithm_selection_string == "EwT" or algorithm_selection_string == "EwTC":
        while True:
            if  algorithm_selection_string == "EwT":
                eligible_projects = [project for project in projects if (sum(project.support) - project.cost) >= 0]
            else:
                eligible_projects = [project for project in projects if (sum(project.support) / project.cost) >= 1]
            while not eligible_projects:
                pLength = len(projects)
                if pLength == 1:
                    eliminated_projects.append(projects[0])
                elimination_with_transfers(projects, doners, listNames, eliminated_projects)
                if len(projects) == pLength:
                    selected_projects = reverse_eliminations(selected_projects, eliminated_projects, budget)
                    return selected_projects
                if  algorithm_selection_string == "EwT":
                    eligible_projects = [project for project in projects if (sum(project.support) - project.cost) >= 0]
                else:
                    eligible_projects = [project for project in projects if (sum(project.support) / project.cost) >= 1]
            if  algorithm_selection_string == "EwT":
                selected_project= select_max_excess_project(projects)
            else:
                selected_project = max(eligible_projects, key=lambda x: sum(x.support) / x.cost)
            excess_support = calculate_excess_support(selected_project)
            if excess_support == 0:
                selected_projects.append(selected_project)
                projects.remove(selected_project)
                budget -= selected_project.cost
                projects = update_projects_support(projects, doners)
                continue
            if excess_support > 0:
                selected_projects.append(selected_project)
                gama = selected_project.get_cost() / (excess_support + selected_project.get_cost())
                projects = distribute_excess_support(projects, selected_project, doners, gama, listNames)
                projects = update_projects_support(projects, doners)
                projects.remove(selected_project)
                budget -= selected_project.cost
                continue

def main():
    # Example projects and doners for testing
    project_A = Project("Project A", 35)
    project_B = Project("Project B", 30)
    project_C = Project("Project C", 35)
    project_D = Project("Project D", 25)
    
    doner1 = Doner([5, 10, 5, 5])
    doner2 = Doner([10, 10, 0, 5])
    doner3 = Doner([0, 15, 5, 5])
    doner4 = Doner([0, 0, 20, 5])
    doner5 = Doner([15, 5, 0, 5])
    
    projects = [project_A, project_B, project_C, project_D]
    doners = [doner1, doner2, doner3, doner4, doner5]
    projects = update_projects_support(projects, doners)
    # Run the participatory budgeting process
    selected_projects = cstv_budgeting(projects, doners, "EwTC")
    # Print the selected projects
    for project in selected_projects:
        print(f"Selected Project: {project.get_name()}, Cost: {project.get_cost()}")

if __name__ == "__main__":
    main()
    # import doctest
    # doctest.testmod()
