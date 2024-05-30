"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achia Ben Natan
Date: 2024/05/16.
"""

import logging
# from pabutools.election import Project, Instance
from typing import List

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
class Project:
    def __init__(self, name: str, cost: int):
        self.name = name
        self.cost = cost
        self.support = []

    def update_support(self, support: List[int]) -> None:
        self.support = support

    def get_name(self) -> str:
        return self.name

    def get_cost(self) -> int:
        return self.cost

    def __str__(self) -> str:
        supporter_strings = ", ".join(str(s) for s in self.support)
        return f"Project: {self.name}, Cost: {self.cost}, Initial support: [{supporter_strings} sum:{sum(self.support)}]"
class Doner:
    def __init__(self, donations: List[int]):
        self.donations = donations

    def get_donations(self) -> List[int]:
        return self.donations

    def update_donations(self, donation: int) -> None:
        self.donations = donation

def get_project_names(projects: List[Project]) -> List[str]:
    return [project.get_name() for project in projects]

def reset_donations(doners: List[Doner], index: int) -> List[Doner]:
    """
    Reset the donations of a donor at the given index to 0.

    Parameters:
    - doners: list of Doner instances
    - index: the index of the donor to reset donations for

    Returns:
    - updated_doners: list of Doner instances with updated donations

    >>> doner1 = Doner([5, 10, 5])
    >>> doner2 = Doner([10, 10, 0])
    >>> doners = [doner1, doner2]
    >>> doners = reset_donations(doners, 1)
    >>> for doner in doners: print(doner.get_donations())
    [5, 0, 5]
    [10, 0, 0]
    """
    for doner in doners:
        doner.donations[index] = 0
    return doners



def distribute_project_support(projects: List[Project], eliminated_project: Project, doners: List[Doner], listNames: List[str]) -> List[Project]:
    """
    Distribute the support of an eliminated project among the remaining projects.

    Parameters:
    - projects: list of Project instances
    - eliminated_project: Project
        The project that has been eliminated.
    - doners: list of Doner instances
    - listNames: list of project names

    Returns:
    - updated_projects: list of Project instances with updated support

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_A.update_support([5, 10, 25])
    >>> project_B.update_support([10, 10, 10])
    >>> doner1 = Doner([5, 10])
    >>> doner2 = Doner([10, 10])
    >>> doners = [doner1, doner2]
    >>> projects = [project_A, project_B]
    >>> updated_projects = distribute_project_support(projects, project_A, doners, get_project_names(projects))
    >>> for project in updated_projects: print(project)
    Project: Project A, Cost: 35, Initial support: [0, 0 sum:0]
    Project: Project B, Cost: 30, Initial support: [13.333333333333332, 15.0 sum:28.333333333333332]
    """
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


def elimination_with_transfers(projects: List[Project], doners: List[Doner], listNames: List[str], eliminated_projects: List[Project]) -> List[Project]:
    """
    Perform the Elimination-with-Transfers (EwT) algorithm on a list of projects with donor support.

    Parameters:
    - projects: list of Project instances
    - doners: list of Doner instances
    - listNames: list of project names
    - eliminated_projects: list of Project instances that have been eliminated
    - alg_str: str
        The algorithm selection string ("EwT" or other).

    Returns:
    - remaining_projects: list of Project instances that are selected for funding

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 35)
    >>> project_D = Project("Project D", 35)
    >>> doner1 = Doner([5, 10, 5, 5])
    >>> doner2 = Doner([10, 10, 0, 5])
    >>> doner3 = Doner([0, 15, 5, 5])
    >>> doner4 = Doner([0, 0, 20, 5])
    >>> doner5 = Doner([15, 5, 0, 5])
    >>> projects = [project_A, project_B, project_C, project_D]
    >>> doners = [doner1, doner2, doner3, doner4, doner5]
    >>> projects = update_projects_support(projects, doners)
    >>> listNames = get_project_names(projects)
    >>> eliminated_projects = []
    >>> remaining_projects = elimination_with_transfers(projects, doners, listNames, eliminated_projects)
    >>> for project in remaining_projects: print(project)
    Project: Project A, Cost: 35, Initial support: [6.0, 12.0, 0.0, 0.0, 18.0 sum:36.0]
    Project: Project B, Cost: 30, Initial support: [12.0, 12.0, 18.0, 0.0, 6.0 sum:48.0]
    Project: Project C, Cost: 35, Initial support: [6.0, 0.0, 6.0, 24.0, 0.0 sum:36.0]
    """
    if len(projects) < 2:
        return projects
    
    while projects:
        # TODO put here also GSC system
        min_project = min(projects, key=lambda p: calculate_excess_support(p))
    
        excess = calculate_excess_support(min_project)

        if excess < 0:
            projects = distribute_project_support(projects, min_project, doners, listNames)
            projects = update_projects_support(projects, doners)
            projects.remove(min_project)
            eliminated_projects.append(min_project)
            break

    return projects
def calculate_total_initial_support(projects: List[Project]) -> int:
    """
    Calculate the total initial support for all projects.

    Parameters:
    - projects: list of Project instances

    Returns:
    - total_initial_support: int
        Total initial support for all projects.

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_A.update_support([5, 10])
    >>> project_B.update_support([10, 10])
    >>> projects = [project_A, project_B]
    >>> calculate_total_initial_support(projects)
    35
    """
    return sum(sum(project.support) for project in projects)

def calculate_total_initial_support_doners(doners: List[Doner]) -> int:
    """
    Calculate the total initial support from all donors.

    Parameters:
    - doners: list of Doner instances

    Returns:
    - total_initial_support_doners: int
        Total initial support from all donors.

    >>> doner1 = Doner([5, 10, 5])
    >>> doner2 = Doner([10, 10, 0])
    >>> doners = [doner1, doner2]
    >>> calculate_total_initial_support_doners(doners)
    40
    """
    return sum(sum(doner.get_donations()) for doner in doners)

def calculate_excess_support(project: Project) -> int:
    """
    Calculate the excess support for a project.

    Parameters:
    - project: Project
        The project to calculate excess support for.

    Returns:
    - excess_support: int
        Excess support for the project.

    >>> project_A = Project("Project A", 35)
    >>> project_A.update_support([5, 10, 25])
    >>> calculate_excess_support(project_A)
    5
    """
    return sum(project.support) - project.cost

def select_max_excess_project(projects: List[Project]) -> Project:
    """
    Select the project with the maximum excess support.

    Parameters:
    - projects: list of Project instances

    Returns:
    - max_excess_project: Project
        Project with the maximum excess support.

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_A.update_support([5, 10, 25])
    >>> project_B.update_support([10, 10, 10])
    >>> projects = [project_A, project_B]
    >>> print(select_max_excess_project(projects))
    Project: Project A, Cost: 35, Initial support: [5, 10, 25 sum:40]
    """
    excess_support = {project: calculate_excess_support(project) for project in projects}
    max_excess_project = max(excess_support, key=excess_support.get)
    return max_excess_project

def distribute_excess_support(projects: List[Project], max_excess_project: Project, doners: List[Doner], gama: float, listNames: List[str]) -> List[Project]:
    """
    Distribute the excess support of the project with maximum excess support.

    Parameters:
    - projects: list of Project instances
    - max_excess_project: Project
        The project with the maximum excess support.
    - doners: list of Doner instances
    - gama: float
        Distribution factor.
    - listNames: list of project names

    Returns:
    - updated_projects: list of Project instances with updated support

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_A.update_support([5, 10, 25])
    >>> project_B.update_support([10, 10, 10])
    >>> doner1 = Doner([5, 10, 5])
    >>> doner2 = Doner([10, 10, 0])
    >>> doners = [doner1, doner2]
    >>> projects = [project_A, project_B]
    >>> projects = distribute_excess_support(projects, project_A, doners, 0.5, get_project_names(projects))
    >>> for project in projects: print(project)
    Project: Project A, Cost: 35, Initial support: [5, 10, 25 sum:40]
    Project: Project B, Cost: 30, Initial support: [10, 10, 10 sum:30]
    """
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

def update_projects_support(projects: List[Project], doners: List[Doner]) -> List[Project]:
    """
    Update the support for each project based on donor donations.

    Parameters:
    - projects: list of Project instances
    - doners: list of Doner instances

    Returns:
    - updated_projects: list of Project instances with updated support

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = Doner([5, 10])
    >>> doner2 = Doner([10, 10])
    >>> doners = [doner1, doner2]
    >>> projects = [project_A, project_B]
    >>> projects = update_projects_support(projects, doners)
    >>> for project in projects: print(project)
    Project: Project A, Cost: 35, Initial support: [5, 10 sum:15]
    Project: Project B, Cost: 30, Initial support: [10, 10 sum:20]
    """
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

def gsc_score(project: Project) -> float:
    """
    Calculate the GSC score for a project.

    Parameters:
    - project: Project
        The project to calculate the GSC score for.
    - L: int
        A parameter related to the budget or total support.
    - n: int
        The number of donors.

    Returns:
    - gsc_score: float
        The GSC score for the project.

    >>> project_A = Project("Project A", 35)
    >>> project_A.update_support([35, 10, 25])
    >>> gsc_score(project_A)
    2.0
    """
    return (sum(project.support) / project.cost)

def find_project_index(listNames: List[str], name: str) -> int:
    """
    Find the index of a project by name in a list of project names.

    Parameters:
    - listNames: list of project names
    - name: str
        The name of the project to find

    Returns:
    - index: int
        The index of the project in the list

    >>> find_project_index(["Project A", "Project B"], "Project B")
    1
    """
    return listNames.index(name)

def reverse_eliminations(selected_projects: List[Project], eliminated_projects: List[Project], budget) -> List[Project]:
    """
    Perform the Reverse Eliminations (RE) procedure.

    Parameters:
    - selected_projects: list of Project instances that are selected for funding
    - eliminated_projects: list of Project instances that have been eliminated
    - budget: remaining budget

    Returns:
    - updated_selected_projects: updated list of Project instances that are selected for funding

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 35)
    >>> project_D = Project("Project D", 35)
    >>> doner1 = Doner([5, 10, 5, 5])
    >>> doner2 = Doner([10, 10, 0, 5])
    >>> doner3 = Doner([0, 15, 5, 5])
    >>> doner4 = Doner([0, 0, 20, 5])
    >>> doner5 = Doner([15, 5, 0, 5])
    >>> projects = [project_A, project_B, project_C,project_D]
    >>> doners = [doner1, doner2, doner3, doner4, doner5]
    >>> projects = update_projects_support(projects, doners)
    >>> selected_projects = [project_A, project_B, project_C]
    >>> eliminated_projects = [project_D]
    >>> projects = reverse_eliminations(selected_projects, eliminated_projects, 35)
    >>> for project in projects: print(project)
    Project: Project A, Cost: 35, Initial support: [5, 10, 0, 0, 15 sum:30]
    Project: Project B, Cost: 30, Initial support: [10, 10, 15, 0, 5 sum:40]
    Project: Project C, Cost: 35, Initial support: [5, 0, 5, 20, 0 sum:30]
    Project: Project D, Cost: 35, Initial support: [5, 5, 5, 5, 5 sum:25]
    """
    for project in reversed(eliminated_projects):
        if project.get_cost() <= budget:
            selected_projects.append(project)
            budget -= project.get_cost()
    return selected_projects


def is_eligible_GE(projects):
    return [project for project in projects if (sum(project.support) - project.cost) >= 0]

def is_eligible_GSC(projects): 
    return [project for project in projects if (sum(project.support) / project.cost) >= 1]



def cstv_budgeting(projects, doners, project_to_fund_selection_procedure,eligible_fn, no_eligible_project_procedure, inclusive_maximality_postprocedure):
    """
    Perform participatory budgeting using the specified functions for selection criteria.

    Parameters:
    - projects: list of Project instances
    - doners: list of Doner instances
    - eligible_fn: function to determine eligible projects
    - select_fn: function to select the project to fund
    - distribute_fn: function to distribute excess support

    Returns:
    - selected_projects: list of Project instances that are selected for funding

    Raises:
    - TypeError: If any element in 'projects' is not an instance of the 'Project' class or any element in 'doners' is not an instance of the 'Doner' class.

    Examples:
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 35)
    >>> project_D = Project("Project D", 35)
    >>> doner1 = Doner([5, 10, 5, 5])
    >>> doner2 = Doner([10, 10, 0, 5])
    >>> doner3 = Doner([0, 15, 5, 5])
    >>> doner4 = Doner([0, 0, 20, 5])
    >>> doner5 = Doner([15, 5, 0, 5])
    >>> projects = [project_A, project_B, project_C, project_D]
    >>> doners = [doner1, doner2, doner3, doner4, doner5]
    >>> projects = update_projects_support(projects, doners)
    >>> selected_projects = cstv_budgeting(projects, doners, select_max_excess_project ,is_eligible_GE, elimination_with_transfers,reverse_eliminations)
    >>> for project in selected_projects:
    ...     print(f"Selected Project: {project.get_name()}, Cost: {project.get_cost()}")
    Selected Project: Project B, Cost: 30
    Selected Project: Project A, Cost: 35
    Selected Project: Project C, Cost: 35
    """

    selected_projects = []
    eliminated_projects = []
    budget = calculate_total_initial_support_doners(doners)
    listNames = get_project_names(projects)

    while True:
        eligible_projects = eligible_fn(projects)
        while not eligible_projects:
            pLength = len(projects)
            if pLength == 1:
                # TODO check this row and find the right number for inside the projects[num]
                eliminated_projects.append(projects[-1])
            no_eligible_project_procedure(projects, doners, listNames, eliminated_projects)
            if len(projects) == pLength:
                selected_projects = inclusive_maximality_postprocedure(selected_projects, eliminated_projects, budget)
                return selected_projects
                

            eligible_projects = eligible_fn(projects)

        selected_project = project_to_fund_selection_procedure(eligible_projects)
        excess_support = calculate_excess_support(selected_project)


        if excess_support >= 0:
            selected_projects.append(selected_project)
            if excess_support > 0:
                gama = selected_project.get_cost() / (excess_support + selected_project.get_cost())
                projects = distribute_excess_support(projects, selected_project, doners, gama, listNames)
            projects = update_projects_support(projects, doners)
            projects.remove(selected_project)
            budget -= selected_project.cost
            continue


def main():
    project_A = Project("Project A", 35)
    project_B = Project("Project B", 30)
    project_C = Project("Project C", 35)
    project_D = Project("Project D", 30)
    
    doner1 = Doner([5, 10, 5, 5])
    doner2 = Doner([10, 10, 0, 5])
    doner3 = Doner([0, 15, 5, 5])
    doner4 = Doner([0, 0, 20, 5])
    doner5 = Doner([15, 5, 0, 5])
    
    projects = [project_A, project_B, project_C, project_D]
    doners = [doner1, doner2, doner3, doner4, doner5]
    projects = update_projects_support(projects, doners)
    selected_projects = cstv_budgeting(projects, doners, select_max_excess_project ,is_eligible_GE, elimination_with_transfers,reverse_eliminations)
    for project in selected_projects:
        print(f"Selected Project: {project.get_name()}, Cost: {project.get_cost()}")
    
if __name__ == "__main__":
    main()
    import doctest
    doctest.testmod()
