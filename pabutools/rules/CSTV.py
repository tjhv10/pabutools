# """
# An implementation of the algorithms in:
# "Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
# Programmer: Achia Ben Natan
# Date: 2024/05/16.
# """
# import logging
# from typing import List

# # Set up logging
# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# class Project:
#     def __init__(self, name: str, cost: int):
#         """
#         Initialize a Project instance.

#         Parameters:
#         - name: str
#             The name of the project.
#         - cost: int
#             The cost of the project.
#         """
#         self.name = name
#         self.cost = cost
#         self.support = []

#     def update_support(self, support: List[int]):
#         """
#         Update the support for the project.

#         Parameters:
#         - support: List[int]
#             The list of support values for the project.
#         """
#         self.support = support

#     def get_name(self) -> str:
#         """
#         Get the name of the project.

#         Returns:
#         - str
#             The name of the project.
#         """
#         return self.name

#     def get_cost(self) -> int:
#         """
#         Get the cost of the project.

#         Returns:
#         - int
#             The cost of the project.
#         """
#         return self.cost

#     def __str__(self):
#         """
#         Return a string representation of the project.

#         Returns:
#         - str
#             A string representation of the project.
#         """
#         supporter_strings = ", ".join(str(s) for s in self.support)
#         return f"Project: {self.name}, Cost: {self.cost}, Initial support: [{supporter_strings} sum:{sum(self.support)}]"

# class Doner:
#     def __init__(self, donations: List[int]):
#         """
#         Initialize a Doner instance.

#         Parameters:
#         - donations: List[int]
#             The list of donations made by the doner.
#         """
#         self.donations = donations

#     def get_donations(self) -> List[int]:
#         """
#         Get the list of donations made by the doner.

#         Returns:
#         - List[int]
#             The list of donations made by the doner.
#         """
#         return self.donations

#     def update_donations(self, donation: List[int]):
#         """
#         Update the donations made by the doner.

#         Parameters:
#         - donation: List[int]
#             The updated list of donations made by the doner.
#         """
#         self.donations = donation

# def get_project_names(projects: List[Project]) -> List[str]:
#     """
#     Get the names of projects from a list of Project instances.

#     Parameters:
#     - projects: List[Project]
#         The list of Project instances.

#     Returns:
#     - List[str]
#         The list of project names.
#     """
#     return [project.get_name() for project in projects]

# def reset_donations(doners: List[Doner], index: int) -> List[Doner]:
#     """
#     Reset the donations of a donor at the given index to 0.

#     Parameters:
#     - doners: List[Doner]
#         The list of Doner instances.
#     - index: int
#         The index of the donor to reset donations for.

#     Returns:
#     - List[Doner]
#         The list of Doner instances with updated donations.
#     """
#     for doner in doners:
#         doner.donations[index] = 0
#     return doners

# def calculate_total_initial_support(projects: List[Project]) -> int:
#     """
#     Calculate the total initial support for all projects.

#     Parameters:
#     - projects: List[Project]
#         The list of Project instances.

#     Returns:
#     - int
#         The total initial support for all projects.
#     """
#     return sum(sum(project.support) for project in projects)

# def calculate_total_initial_support_doners(doners: List[Doner]) -> int:
#     """
#     Calculate the total initial support from all donors.

#     Parameters:
#     - doners: List[Doner]
#         The list of Doner instances.

#     Returns:
#     - int
#         The total initial support from all donors.
#     """
#     return sum(sum(doner.get_donations()) for doner in doners)

# def calculate_excess_support(project):
#     return sum(project.support) - project.cost

# def select_max_excess_project(projects):
#     excess_support = {project: calculate_excess_support(project) for project in projects}
#     max_excess_project = max(excess_support, key=excess_support.get)
#     return max_excess_project

# def distribute_excess_support(projects, max_excess_project, doners, gama, listNames):
#     max_index = find_project_index(listNames, max_excess_project.get_name())
#     for doner in doners:
#         toDistribute = doner.get_donations()[max_index] * (1 - gama)
#         doner.get_donations()[max_index] = 0
#         total = sum(doner.get_donations())
#         for i, donetion in enumerate(doner.get_donations()):
#             if i != max_index:
#                 if total != 0:
#                     part = donetion / total
#                     doner.get_donations()[i] = donetion + toDistribute * part
#     return projects

# def update_projects_support(projects, doners):
#     indexes_to_go_over = []
#     for i, doner in enumerate(doners):
#         if sum(doner.get_donations()) > 0:
#             indexes_to_go_over.append(i)
#     if len(indexes_to_go_over) == 0:
#         return projects
#     index = 0
#     for i, project in enumerate(projects):
#         don = []
#         for doner in doners:
#             don.append(doner.get_donations()[indexes_to_go_over[index]])
#         project.update_support(don)
#         index += 1
#     return projects

# def get_project_names(projects):
#     """
#     Get the names of projects from a list of Project instances.

#     Parameters:
#     - projects: list of Project instances

#     Returns:
#     - project_names: list of project names
#     """
#     return [project.get_name() for project in projects]

# def gsc_score(project, L, n):
#     cost = project.get_cost()
#     support = sum(project.support)
#     return (1 / cost) * (support * (L / n))

# def select_gsc_project(projects, L, n):
#     gsc_scores = {project: gsc_score(project, L, n) for project in projects}
#     max_gsc_project = max(gsc_scores, key=gsc_scores.get)
#     return max_gsc_project

# def update_donors_with_project_support(projects, doners):
#     """
#     Update the donations of donors based on the support for each project.

#     Parameters:
#     - projects: list of Project instances
#     - doners: list of Doner instances

#     Returns:
#     - updated_doners: list of Doner instances with updated donations
#     """
#     for i, doner in enumerate(doners):
#         updated_donations = [project.support[i] for project in projects]
#         doner.update_donations(updated_donations)
#     return doners

# def distribute_project_support(projects, eliminated_project, doners, listNames):
#     max_index = find_project_index(listNames, eliminated_project.get_name())
#     for doner in doners:
#         toDistribute = doner.get_donations()[max_index]
#         total = sum(doner.get_donations())
#         if total == 0:
#             continue
#         for i, donetion in enumerate(doner.get_donations()):
#             if i != max_index:
#                 part = donetion / total
#                 doner.get_donations()[i] = donetion + toDistribute * part
#     doners = reset_donations(doners, max_index)
#     return update_projects_support(projects, doners)

# def find_project_index(listNames, project_name):
#     return next((i for i, project in enumerate(listNames) if project == project_name), -1)

# def elimination_with_transfers(projects, doners, listNames, eliminated_projects,alg_str):
#     """
#     Perform the Elimination-with-Transfers (EwT) algorithm on a list of projects with donor support.

#     Parameters:
#     - projects: list of Project instances
#     - doners: list of Doner instances
#     - eliminated_projects: list of Project instances that have been eliminated

#     Returns:
#     - selected_projects: list of Project instances that are selected for funding
#     """
#     if len(projects) < 2:
#         return projects
    
#     while projects:
#         if alg_str =="EwT":
#             # Select the project with the minimum excess support
#             min_project = min(projects, key=lambda p: calculate_excess_support(p))
#         else:
#             min_project = min(projects, key=lambda p: calculate_excess_support(p)/p.cost)
#         # Calculate excess support of the selected project
#         excess = calculate_excess_support(min_project)

#         if excess < 0:
#             # Eliminate the project with minimum excess support
#             projects = distribute_project_support(projects, min_project, doners, listNames)
#             projects = update_projects_support(projects, doners)
#             projects.remove(min_project)
#             eliminated_projects.append(min_project)
#             break

#     return projects

# def reverse_eliminations(selected_projects, eliminated_projects, budget):
#     """
#     Perform the Reverse Eliminations (RE) procedure.

#     Parameters:
#     - selected_projects: list of Project instances that are selected for funding
#     - eliminated_projects: list of Project instances that have been eliminated
#     - budget: remaining budget

#     Returns:
#     - selected_projects: updated list of Project instances that are selected for funding
#     """
#     for project in reversed(eliminated_projects):
#         if project.get_cost() <= budget:
#             selected_projects.append(project)
#             budget -= project.get_cost()
#     return selected_projects

# def cstv_budgeting(projects, doners, algorithm_selection_string):
#     if not all(isinstance(project, Project) for project in projects):
#         raise TypeError("All elements in the 'projects' list must be instances of the 'Project' class.")
#     if not all(isinstance(doner, Doner) for doner in doners):
#         raise TypeError("All elements in the 'doners' list must be instances of the 'Doner' class.")

#     selected_projects = []
#     eliminated_projects = []
#     budget = calculate_total_initial_support_doners(doners)
#     listNames = get_project_names(projects)
#     if algorithm_selection_string == "EwT" or algorithm_selection_string == "EwTC":
#         while True:
#             if  algorithm_selection_string == "EwT":
#                 eligible_projects = [project for project in projects if (sum(project.support) - project.cost) >= 0]
#             else:
#                 eligible_projects = [project for project in projects if (sum(project.support) / project.cost) >= 1]
#             while not eligible_projects:
#                 pLength = len(projects)
#                 if pLength == 1:
#                     eliminated_projects.append(projects[0])
#                 elimination_with_transfers(projects, doners, listNames, eliminated_projects,algorithm_selection_string)
#                 if len(projects) == pLength:
#                     selected_projects = reverse_eliminations(selected_projects, eliminated_projects, budget)
#                     return selected_projects
#                 if  algorithm_selection_string == "EwT":
#                     eligible_projects = [project for project in projects if (sum(project.support) - project.cost) >= 0]
#                 else:
#                     eligible_projects = [project for project in projects if (sum(project.support) / project.cost) >= 1]
#             if  algorithm_selection_string == "EwT":
#                 selected_project= select_max_excess_project(projects)
#             else:
#                 selected_project = max(eligible_projects, key=lambda x: sum(x.support) / x.cost)
#             excess_support = calculate_excess_support(selected_project)
#             if excess_support == 0:
#                 selected_projects.append(selected_project)
#                 projects.remove(selected_project)
#                 budget -= selected_project.cost
#                 projects = update_projects_support(projects, doners)
#                 continue
#             if excess_support > 0:
#                 selected_projects.append(selected_project)
#                 gama = selected_project.get_cost() / (excess_support + selected_project.get_cost())
#                 projects = distribute_excess_support(projects, selected_project, doners, gama, listNames)
#                 projects = update_projects_support(projects, doners)
#                 projects.remove(selected_project)
#                 budget -= selected_project.cost
#                 continue
#     # elif algorithm_selection_string == "MT" or algorithm_selection_string == "MTC":
        

#     return selected_projects

# def main():
#     # Example projects and doners for testing
#     project_A = Project("Project A", 35)
#     project_B = Project("Project B", 30)
#     project_C = Project("Project C", 35)
#     project_D = Project("Project D", 25)
    
#     doner1 = Doner([5, 10, 5, 5])
#     doner2 = Doner([10, 10, 0, 5])
#     doner3 = Doner([0, 15, 5, 5])
#     doner4 = Doner([0, 0, 20, 5])
#     doner5 = Doner([15, 5, 0, 5])
    
#     projects = [project_A, project_B, project_C, project_D]
#     doners = [doner1, doner2, doner3, doner4, doner5]
#     projects = update_projects_support(projects, doners)
#     # Run the participatory budgeting process
#     selected_projects = cstv_budgeting(projects, doners, "EwTC")
#     # Print the selected projects
#     for project in selected_projects:
#         print(f"Selected Project: {project.get_name()}, Cost: {project.get_cost()}")

# if __name__ == "__main__":
#     main()
#     # import doctest
#     # doctest.testmod()






















import logging
from typing import List, Callable, Collection, Iterable

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

class Project:
    def __init__(self, name: str, cost: int):
        self.name = name
        self.cost = cost
        self.support = []

    def update_support(self, support: List[int]) -> None:
        """
        Update the support for the project.

        Parameters:
        - support: List[int]
            List of support values from each donor.
        """
        self.support = support

    def get_name(self) -> str:
        """
        Get the name of the project.
        """
        return self.name

    def get_cost(self) -> int:
        """
        Get the cost of the project.
        """
        return self.cost

    def __str__(self) -> str:
        supporter_strings = ", ".join(str(s) for s in self.support)
        return f"Project: {self.name}, Cost: {self.cost}, Initial support: [{supporter_strings} sum:{sum(self.support)}]"

class Doner:
    def __init__(self, donations: List[int]):
        self.donations = donations

    def get_donations(self) -> List[int]:
        """
        Get the donations of the donor.
        """
        return self.donations

    def update_donations(self, donation: int) -> None:
        """
        Update the donations of the donor.

        Parameters:
        - donation: int
            Donation value.
        """
        self.donations = donation


def get_project_names(projects: List[Project]) -> List[str]:
    """
    Get the names of projects from a list of Project instances.

    Parameters:
    - projects: list of Project instances

    Returns:
    - project_names: list of project names

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> projects = [project_A, project_B]
    >>> get_project_names(projects)
    ['Project A', 'Project B']
    """
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
    >>> reset_donations(doners, 1)
    [<__main__.Doner object at ...>, <__main__.Doner object at ...>]
    >>> [doner.get_donations() for doner in doners]
    [[5, 0, 5], [10, 0, 0]]
    """
    for doner in doners:
        doner.donations[index] = 0
    return doners

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
    >>> select_max_excess_project(projects).get_name()
    'Project A'
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
    >>> distribute_excess_support(projects, project_A, doners, 0.5, get_project_names(projects))
    [<__main__.Project object at ...>, <__main__.Project object at ...>]
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
    >>> update_projects_support(projects, doners)
    >>> projects[0].support
    [5, 10]
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

def gsc_score(project: Project, L: int, n: int) -> float:
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
    >>> project_A.update_support([5, 10, 25])
    >>> gsc_score(project_A, 50, 3)
    1.4285714285714286
    """
    cost = project.get_cost()
    support = sum(project.support)
    return (1 / cost) * (support * (L / n))

def select_gsc_project(projects: List[Project], L: int, n: int) -> Project:
    """
    Select the project with the highest GSC score.

    Parameters:
    - projects: list of Project instances
    - L: int
        A parameter related to the budget or total support.
    - n: int
        The number of donors.

    Returns:
    - max_gsc_project: Project
        Project with the highest GSC score.

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_A.update_support([5, 10, 25])
    >>> project_B.update_support([10, 10, 10])
    >>> projects = [project_A, project_B]
    >>> select_gsc_project(projects, 50, 3).get_name()
    'Project A'
    """
    gsc_scores = {project: gsc_score(project, L, n) for project in projects}
    max_gsc_project = max(gsc_scores, key=gsc_scores.get)
    return max_gsc_project

def update_donors_with_project_support(projects: List[Project], doners: List[Doner]) -> List[Doner]:
    """
    Update the donations of donors based on the support for each project.

    Parameters:
    - projects: list of Project instances
    - doners: list of Doner instances

    Returns:
    - updated_doners: list of Doner instances with updated donations

    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_A.update_support([5, 10, 25])
    >>> project_B.update_support([10, 10, 10])
    >>> doner1 = Doner([5, 10])
    >>> doner2 = Doner([10, 10])
    >>> doners = [doner1, doner2]
    >>> projects = [project_A, project_B]
    >>> update_donors_with_project_support(projects, doners)
    [<__main__.Doner object at ...>, <__main__.Doner object at ...>]
    >>> [doner.get_donations() for doner in doners]
    [[5, 10], [10, 10]]
    """
    for i, doner in enumerate(doners):
        updated_donations = [project.support[i] for project in projects]
        doner.update_donations(updated_donations)
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
    >>> distribute_project_support(projects, project_A, doners, get_project_names(projects))
    [<__main__.Project object at ...>, <__main__.Project object at ...>]
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

def find_project_index(listNames: List[str], project_name: str) -> int:
    """
    Find the index of a project in the list of project names.

    Parameters:
    - listNames: list of project names
    - project_name: str
        The name of the project to find.

    Returns:
    - index: int
        The index of the project in the list, or -1 if not found.

    >>> find_project_index(['Project A', 'Project B'], 'Project A')
    0
    >>> find_project_index(['Project A', 'Project B'], 'Project C')
    -1
    """
    return next((i for i, project in enumerate(listNames) if project == project_name), -1)

def elimination_with_transfers(projects: List[Project], doners: List[Doner], listNames: List[str], eliminated_projects: List[Project], alg_str: str) -> List[Project]:
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
    >>> doner1 = Doner([5, 10])
    >>> doner2 = Doner([10, 10])
    >>> projects = [project_A, project_B]
    >>> doners = [doner1, doner2]
    >>> elimination_with_transfers(projects, doners, get_project_names(projects), [], "EwT")
    [<__main__.Project object at ...>, <__main__.Project object at ...>]
    """
    if len(projects) < 2:
        return projects
    
    while projects:
        if alg_str == "EwT":
            min_project = min(projects, key=lambda p: calculate_excess_support(p))
        else:
            min_project = min(projects, key=lambda p: calculate_excess_support(p) / p.cost)
        
        excess = calculate_excess_support(min_project)

        if excess < 0:
            projects = distribute_project_support(projects, min_project, doners, listNames)
            projects = update_projects_support(projects, doners)
            projects.remove(min_project)
            eliminated_projects.append(min_project)
            break

    return projects

def reverse_eliminations(selected_projects: List[Project], eliminated_projects: List[Project], budget: int) -> List[Project]:
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
    >>> selected_projects = [project_A]
    >>> eliminated_projects = [project_B]
    >>> reverse_eliminations(selected_projects, eliminated_projects, 30)
    [<__main__.Project object at ...>, <__main__.Project object at ...>]
    """
    for project in reversed(eliminated_projects):
        if project.get_cost() <= budget:
            selected_projects.append(project)
            budget -= project.get_cost()
    return selected_projects

def cstv_budgeting(projects, doners, algorithm_selection_string):
    """
    Perform participatory budgeting using the specified algorithm.

    Parameters:
    - projects: list of Project instances
    - doners: list of Doner instances
    - algorithm_selection_string: string indicating which algorithm to use ("EwT" or "EwTC")

    Returns:
    - selected_projects: list of Project instances that are selected for funding

    Raises:
    - TypeError: If any element in 'projects' is not an instance of the 'Project' class or any element in 'doners' is not an instance of the 'Doner' class.

    Examples:
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 25)
    >>> project_D = Project("Project D", 20)
    >>> doner1 = Doner([10, 20, 5, 0])
    >>> doner2 = Doner([15, 5, 10, 10])
    >>> doner3 = Doner([10, 5, 15, 10])
    >>> projects = [project_A, project_B, project_C, project_D]
    >>> doners = [doner1, doner2, doner3]
    >>> projects = update_projects_support(projects, doners)
    >>> selected_projects = cstv_budgeting(projects, doners, "EwT")
    >>> len(selected_projects) > 5
    True
    >>> all(isinstance(p, Project) for p in selected_projects)
    True
    """
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
            if algorithm_selection_string == "EwT":
                eligible_projects = [project for project in projects if (sum(project.support) - project.cost) >= 0]
            else:
                eligible_projects = [project for project in projects if (sum(project.support) / project.cost) >= 1]

            while not eligible_projects:
                pLength = len(projects)
                if pLength == 1:
                    eliminated_projects.append(projects[0])
                elimination_with_transfers(projects, doners, listNames, eliminated_projects, algorithm_selection_string)
                if len(projects) == pLength:
                    selected_projects = reverse_eliminations(selected_projects, eliminated_projects, budget)
                    return selected_projects

                if algorithm_selection_string == "EwT":
                    eligible_projects = [project for project in projects if (sum(project.support) - project.cost) >= 0]
                else:
                    eligible_projects = [project for project in projects if (sum(project.support) / project.cost) >= 1]

            if algorithm_selection_string == "EwT":
                selected_project = select_max_excess_project(projects)
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

    return selected_projects
if __name__ == "__main__":
    import doctest
    doctest.testmod()