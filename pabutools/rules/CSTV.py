import logging
from pabutools.election import Project, CumulativeBallot
from typing import List

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def find_project_index(listNames: List[str], name: str) -> int:
    """
    Finds the index of a project name in the list of project names.

    Parameters
    ----------
    listNames : List[str]
        The list of project names.
    name : str
        The name of the project to find.

    Returns
    -------
    int
        The index of the project name in the list.

    Examples
    --------
    >>> find_project_index(["Project A", "Project B", "Project C"], "Project B")
    1
    """
    return listNames.index(name)

def reset_donations(doners: List[CumulativeBallot], index: str) -> List[CumulativeBallot]:
    """
    Resets the donations for the eliminated project.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    index : str
        The name of the project to reset donations for.

    Returns
    -------
    List[CumulativeBallot]
        The updated list of doner ballots with reset donations.

    Examples
    --------
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> reset_donations([doner1, doner2], "Project A")
    [{'Project A': 0, 'Project B': 10}, {'Project A': 0, 'Project B': 0}]
    """
    logging.debug(f"Resetting donations for eliminated project: {index}")
    for doner in doners:
        doner[index] = 0
    return doners

def get_project_names(projects: List[Project]) -> List[str]:
    """
    Gets the names of all projects.

    Parameters
    ----------
    projects : List[Project]
        The list of projects.

    Returns
    -------
    List[str]
        The list of project names.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> get_project_names([project_A, project_B])
    ['Project A', 'Project B']
    """
    return [project.name for project in projects]

def distribute_project_support(projects: List[Project], eliminated_project: Project, doners: List[CumulativeBallot], listNames: List[str]) -> List[Project]:
    """
    Distributes the support of an eliminated project to the remaining projects.

    Parameters
    ----------
    projects : List[Project]
        The list of projects.
    eliminated_project : Project
        The project that has been eliminated.
    doners : List[CumulativeBallot]
        The list of doner ballots.
    listNames : List[str]
        The list of project names.

    Returns
    -------
    List[Project]
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0, "Project C": 5})
    >>> distribute_project_support([project_A, project_B, project_C], project_A, [doner1, doner2], ["Project A", "Project B", "Project C"])
    [Project A, Project B, Project C]
    """
    eliminated_name = eliminated_project.name
    logging.debug(f"Distributing support of eliminated project: {eliminated_name}")
    for doner in doners:
        toDistribute = doner[eliminated_name]
        total = sum(doner.values())
        if total == 0:
            continue
        for i, donation in enumerate(doner.values()):
            if listNames[i] != eliminated_name:
                part = donation / total
                doner[listNames[i]] = donation + toDistribute * part
    doners = reset_donations(doners, eliminated_name)
    return projects

def distribute_excess_support(projects: List[Project], max_excess_project: Project, doners: List[CumulativeBallot], gama: float, listNames: List[str]) -> List[Project]:
    """
    Distributes the excess support of a selected project to the remaining projects.

    Parameters
    ----------
    projects : List[Project]
        The list of projects.
    max_excess_project : Project
        The project with the maximum excess support.
    doners : List[CumulativeBallot]
        The list of doner ballots.
    gama : float
        The proportion to distribute.
    listNames : List[str]
        The list of project names.

    Returns
    -------
    List[Project]
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0, "Project C": 5})
    >>> distribute_excess_support([project_A, project_B, project_C], project_A, [doner1, doner2], 0.5, ["Project A", "Project B", "Project C"])
    [Project A, Project B, Project C]
    """
    max_project_name = max_excess_project.name
    logging.debug(f"Distributing excess support of selected project: {max_project_name}")
    for doner in doners:
        doner_copy = doner.copy()
        toDistribute = doner_copy[max_project_name] * (1 - gama)
        doner[max_project_name] = 0
        doner_copy[max_project_name] = 0
        total = sum(doner_copy.values())
        for i, donation in enumerate(doner_copy.values()):
            if listNames[i] != max_project_name:
                if total != 0:
                    part = donation / total
                    doner[listNames[i]] = donation + toDistribute * part
                    
    return projects

def calculate_total_support_for_project(doners: List[CumulativeBallot], project: Project) -> float:
    """
    Calculates the total support for a given project.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    project : Project
        The project to calculate support for.

    Returns
    -------
    float
        The total support for the project.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> calculate_total_support_for_project([doner1, doner2], project_A)
    15
    """
    return sum(doner.get(project.name, 0) for doner in doners)

def calculate_total_initial_support(doners: List[CumulativeBallot], projects: List[Project]) -> int:
    """
    Calculates the total initial support for all projects.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.

    Returns
    -------
    int
        The total initial support for all projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> calculate_total_initial_support([doner1, doner2], [project_A, project_B])
    25
    """
    return sum(calculate_total_support_for_project(doners, project) for project in projects)

def calculate_total_initial_support_doners(doners: List[CumulativeBallot]) -> int:
    """
    Calculates the total initial support from all doners.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.

    Returns
    -------
    int
        The total initial support from all doners.

    Examples
    --------
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> calculate_total_initial_support_doners([doner1, doner2])
    25
    """
    return sum(sum(doner.values()) for doner in doners)

def is_eligible_GE(doners: List[CumulativeBallot], projects: List[Project]) -> List[Project]:
    """
    Determines the eligible projects based on the General Election (GE) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.

    Returns
    -------
    List[Project]
        The list of eligible projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> is_eligible_GE([doner1, doner2], [project_A, project_B])
    []
    """
    return [project for project in projects if (calculate_total_support_for_project(doners, project) - project.cost) >= 0]

def is_eligible_GSC(doners: List[CumulativeBallot], projects: List[Project]) -> List[Project]: 
    """
    Determines the eligible projects based on the Greatest Support to Cost (GSC) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.

    Returns
    -------
    List[Project]
        The list of eligible projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> is_eligible_GSC([doner1, doner2], [project_A, project_B])
    []
    """
    return [project for project in projects if (calculate_total_support_for_project(doners, project) / project.cost) >= 1]

def calculate_excess_support(doners: List[CumulativeBallot], project: Project) -> int:
    """
    Calculates the excess support for a given project.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    project : Project
        The project to calculate excess support for.

    Returns
    -------
    int
        The excess support for the project.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> calculate_excess_support([doner1, doner2], project_A)
    -20
    """
    return calculate_total_support_for_project(doners, project) - project.cost

def calculate_ratio_support(doners: List[CumulativeBallot], project: Project) -> float:
    """
    Calculates the ratio of support to cost for a given project.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    project : Project
        The project to calculate the ratio for.

    Returns
    -------
    float
        The ratio of support to cost for the project.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> calculate_ratio_support([doner1, doner2], project_A)
    0.42857142857142855
    """
    return calculate_total_support_for_project(doners, project) / project.cost

def select_project_GE(doners: List[CumulativeBallot], projects: List[Project]) -> Project:
    """
    Selects the project with the maximum excess support using the General Election (GE) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.

    Returns
    -------
    Project
        The selected project.

    Examples
    --------
    >>> project_A = Project("Project A", 36)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> select_project_GE([doner1, doner2], [project_A, project_B]).name
    'Project B'
    """
    excess_support = {project: calculate_excess_support(doners, project) for project in projects}
    max_excess_project = max(excess_support, key=excess_support.get)
    logging.debug(f"Selected project by GE method: {max_excess_project.name}")
    return max_excess_project

def select_project_GSC(doners: List[CumulativeBallot], projects: List[Project]) -> Project:
    """
    Selects the project with the maximum ratio of support to cost using the Greatest Support to Cost (GSC) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.

    Returns
    -------
    Project
        The selected project.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> select_project_GSC([doner1, doner2], [project_A, project_B]).name
    'Project A'
    """
    ratio_support = {project: calculate_ratio_support(doners, project) for project in projects}
    max_ratio_project = max(ratio_support, key=ratio_support.get)
    logging.debug(f"Selected project by GSC method: {max_ratio_project.name}")
    return max_ratio_project

def elimination_with_transfers(doners: List[CumulativeBallot], projects: List[Project], listNames: List[str], eliminated_projects: List[Project], _: callable) -> List[Project]:
    """
    Eliminates the project with the least excess support and redistributes its support to the remaining projects.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.
    listNames : List[str]
        The list of project names.
    eliminated_projects : List[Project]
        The list of eliminated projects.
    _ : callable
        A placeholder for a callable function.

    Returns
    -------
    List[Project]
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0, "Project C": 5})
    >>> elimination_with_transfers([doner1, doner2], [project_A, project_B, project_C], ["Project A", "Project B", "Project C"], [], None)
    True
    >>> print(doner1["Project A"])
    0
    >>> print(doner1["Project B"])
    12.5
    >>> print(doner2["Project A"])
    0
    >>> print(doner2["Project B"])
    0.0
    >>> print(doner1["Project C"])
    6.25
    >>> print(doner2["Project C"])
    8.333333333333332

    """
    if len(projects) < 2:
        logging.debug("Not enough projects to eliminate.")
        return False

    min_project = min(projects, key=lambda p: calculate_excess_support(doners, p))
    logging.debug(f"Eliminating project with least excess support: {min_project.name}")
    projects = distribute_project_support(projects, min_project, doners, listNames)
    projects.remove(min_project)
    eliminated_projects.append(min_project)
    return True

def minimal_transfer(doners: List[CumulativeBallot], projects: List[Project], listNames, eliminated_projects, project_to_fund_selection_procedure: callable) -> List[Project]:
    """
    Performs minimal transfer of donations to reach the required support for a selected project.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.
    listNames : List[str]
        The list of project names.
    eliminated_projects : List[Project]
        The list of eliminated projects.
    project_to_fund_selection_procedure : callable
        The procedure to select a project for funding.

    Returns
    -------
    List[Project]
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> minimal_transfer([doner1, doner2], [project_A, project_B], ["Project A", "Project B"], [], select_project_GE)
    False
    >>> print(doner1["Project A"])
    15.0
    >>> print(doner1["Project B"])
    0.0
    >>> print(doner2["Project A"])
    10
    >>> print(doner2["Project B"])
    0
    """
    chosen_project = project_to_fund_selection_procedure(doners, projects)
    logging.debug(f"Selected project for minimal transfer: {chosen_project.name}")
    r = calculate_total_support_for_project(doners, chosen_project) / chosen_project.cost
    doners_of_selected_project = [doner for doner in doners if (doner.get(chosen_project.name, 0)) > 0]
    while r < 1:
        flag = True
        for doner in doners_of_selected_project:
            if sum(doner.values()) != doner.get(chosen_project.name, 0):
                flag = False
                break
        if flag:
            return False
        for doner in doners_of_selected_project:
            total = sum(doner.values()) - doner.get(chosen_project.name, 0)
            to_distribute = min(total, doner.get(chosen_project.name) / r - doner.get(chosen_project.name, 0))
            for project_name, donation in doner.items():
                if project_name != chosen_project.name and total > 0:
                    part = donation / total
                    change = to_distribute * part
                    doner[project_name] -= change
                    doner[chosen_project.name] += change
        r = calculate_total_support_for_project(doners, chosen_project) / chosen_project.cost
    return True

def reverse_eliminations(doners: List[CumulativeBallot], selected_projects: List[Project], eliminated_projects: List[Project], _: callable, budget: int) -> List[Project]:
    """
    Reverses eliminations of projects if the budget allows.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    selected_projects : List[Project]
        The list of selected projects.
    eliminated_projects : List[Project]
        The list of eliminated projects.
    _ : callable
        A placeholder for a callable function.
    budget : int
        The remaining budget.

    Returns
    -------
    List[Project]
        The updated list of selected projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> selected_projects = [project_A]
    >>> eliminated_projects = [project_B]
    >>> reverse_eliminations([], selected_projects, eliminated_projects, None, 30)
    [Project A, Project B]
    """
    for project in reversed(eliminated_projects):
        if project.cost <= budget:
            selected_projects.append(project)
            budget -= project.cost
    return selected_projects

def acceptance_of_undersupported_projects(doners: List[CumulativeBallot], selected_projects: List[Project], eliminated_projects: List[Project], project_to_fund_selection_procedure: callable, budget: int) -> List[Project]:
    """
    Accepts undersupported projects if the budget allows.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    selected_projects : List[Project]
        The list of selected projects.
    eliminated_projects : List[Project]
        The list of eliminated projects.
    project_to_fund_selection_procedure : callable
        The procedure to select a project for funding.
    budget : int
        The remaining budget.

    Returns
    -------
    List[Project]
        The updated list of selected projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 20)
    >>> selected_projects = [project_A]
    >>> eliminated_projects = [project_B, project_C]
    >>> selected = acceptance_of_undersupported_projects([], selected_projects, eliminated_projects, select_project_GE, 25)
    """
    while len(eliminated_projects) != 0:
        selected_project = project_to_fund_selection_procedure(doners, eliminated_projects)
        if selected_project.cost < budget:
            selected_projects.append(selected_project)
            eliminated_projects.remove(selected_project)
            budget -= selected_project.cost
        else:
            eliminated_projects.remove(selected_project)
    return selected_projects
def cstv_budgeting_combination(doners: List[CumulativeBallot], projects: List[Project], combination: str) -> List[Project]:
    """
    Runs the CSTV test based on the combination of functions provided.

    Parameters
    ----------
    combination : str
        The combination of CSTV functions to run.

    Returns
    -------
    List[Project]
        The selected projects.

    Examples
    --------
    >>> combination = "GE-GE-GE"
    >>> run_cstv_test_combination(combination)
    ['Project B', 'Project C']
    """
    if combination =="EwT" or combination =="ewt" or combination =="EWT":
        return cstv_budgeting(doners, projects, select_project_GE, is_eligible_GE, elimination_with_transfers, reverse_eliminations)
    elif combination =="EwTC" or combination =="ewtc" or combination =="EWTC":
        return cstv_budgeting(doners, projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
    elif combination =="MT" or combination =="mt":
        return cstv_budgeting(doners, projects, select_project_GE, is_eligible_GE, minimal_transfer, acceptance_of_undersupported_projects)
    elif combination =="MTC" or combination =="mtc":
        return cstv_budgeting(doners, projects, select_project_GSC, is_eligible_GSC, minimal_transfer, acceptance_of_undersupported_projects)
    else:
        print("Insert a correct combination algorithm")



def cstv_budgeting(doners: List[CumulativeBallot], projects: List[Project], project_to_fund_selection_procedure: callable, eligible_fn: callable,
                    no_eligible_project_procedure: callable, inclusive_maximality_postprocedure: callable) -> List[Project]:
    """
    The CSTV (Cumulative Support Transfer Voting) budgeting algorithm to select projects based on doner ballots.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : List[Project]
        The list of projects.
    project_to_fund_selection_procedure : callable
        The procedure to select a project for funding.
    eligible_fn : callable
        The function to determine eligible projects.
    no_eligible_project_procedure : callable
        The procedure when there are no eligible projects.
    inclusive_maximality_postprocedure : callable
        The post procedure to handle inclusive maximality.

    Returns
    -------
    List[Project]
        The list of selected projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 20)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 10, "Project C": 0})
    >>> doner3 = CumulativeBallot({"Project A": 0, "Project B": 15, "Project C": 5})
    >>> doner4 = CumulativeBallot({"Project A": 0, "Project B": 0, "Project C": 20})
    >>> doner5 = CumulativeBallot({"Project A": 15, "Project B": 5, "Project C": 0})
    >>> projects = [project_A, project_B, project_C]
    >>> doners = [doner1, doner2, doner3, doner4, doner5]
    >>> project_to_fund_selection_procedure = select_project_GE
    >>> eligible_fn = is_eligible_GE
    >>> no_eligible_project_procedure = elimination_with_transfers
    >>> inclusive_maximality_postprocedure = reverse_eliminations
    >>> cstv_budgeting(doners, projects, project_to_fund_selection_procedure, eligible_fn, no_eligible_project_procedure, inclusive_maximality_postprocedure)
    [Project B, Project C]
    """
    selected_projects = []
    eliminated_projects = []
    budget = calculate_total_initial_support_doners(doners)
    listNames = get_project_names(projects)
    
    logging.debug("Initial budget: %s" % budget)

    while True:
        if not projects:
            return selected_projects
        eligible_projects = eligible_fn(doners, projects)
        logging.debug("Eligible projects: %s" % [project.name for project in eligible_projects])
        
        # Log donors and total donations for each project
        for project in projects:
            donations = sum(doner[project.name] for doner in doners)
            logging.debug("Donors and total donations for %s: %s" % (project.name, donations))
        
        while not eligible_projects:
            flag = no_eligible_project_procedure(doners, projects, listNames, eliminated_projects, project_to_fund_selection_procedure)
            if not flag:
                selected_projects = inclusive_maximality_postprocedure(doners, selected_projects, eliminated_projects, project_to_fund_selection_procedure, budget)
                logging.debug("Final selected projects: %s" % [project.name for project in selected_projects])
                return selected_projects
            eligible_projects = eligible_fn(doners, projects)
        selected_project = project_to_fund_selection_procedure(doners, eligible_projects)
        excess_support = calculate_excess_support(doners, selected_project)
        logging.debug("Excess support for %s: %s" % (selected_project.name, excess_support))

        if excess_support >= 0:
            selected_projects.append(selected_project)
            logging.debug("Updated selected projects: %s" % [project.name for project in selected_projects])
            if excess_support > 0:
                gama = selected_project.cost / (excess_support + selected_project.cost)
                projects = distribute_excess_support(projects, selected_project, doners, gama, listNames)
            else:
                reset_donations(doners,selected_project.name)

            projects.remove(selected_project)
            budget -= selected_project.cost
            logging.debug(f"Remaining budget: {budget}")
            continue

def main():
    project_A = Project("Project A", 35)
    project_B = Project("Project B", 30)
    project_C = Project("Project C", 30)
    project_D = Project("Project D", 30)
    
    doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5, "Project D": 5})
    doner2 = CumulativeBallot({"Project A": 10, "Project B": 10, "Project C": 0, "Project D": 5})
    doner3 = CumulativeBallot({"Project A": 0, "Project B": 15, "Project C": 5, "Project D": 5})
    doner4 = CumulativeBallot({"Project A": 0, "Project B": 0, "Project C": 20, "Project D": 5})
    doner5 = CumulativeBallot({"Project A": 15, "Project B": 5, "Project C": 0, "Project D": 5})

    projects = [project_A, project_B, project_C, project_D]
    doners = [doner1, doner2, doner3, doner4, doner5]

    
    selected_projects = cstv_budgeting_combination(doners, projects,"ewtc")
    logging.debug(f"Selected projects: {[project.name for project in selected_projects]}")
    for project in selected_projects:
        print(project.name)


if __name__ == "__main__":
    main()
