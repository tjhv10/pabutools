"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achia Ben Natan
Date: 2024/05/16.
"""

import logging
from pabutools.election import Project, CumulativeBallot ,Instance
from typing import List



###################################################################
#                                                                 #
#                     Main algorithm                              #
#                                                                 #
###################################################################


def cstv_budgeting(doners: List[CumulativeBallot], projects: Instance, project_to_fund_selection_procedure: callable, eligible_fn: callable,
                    no_eligible_project_procedure: callable, inclusive_maximality_postprocedure: callable) -> Instance:
    """
    The CSTV (Cumulative Support Transfer Voting) budgeting algorithm to select projects based on doner ballots.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : Instance
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
    Instance
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
    >>> len(cstv_budgeting(doners, projects, project_to_fund_selection_procedure, eligible_fn, no_eligible_project_procedure, inclusive_maximality_postprocedure))
    3
    """
    eliminated_projects = []
    if not check_equal_donations(doners):
        logger.warning("Not all doners donate the same amount. Change the donations and try again.")
        return
    S = Instance([])
    while True:
        budget = sum(sum(doner.values()) for doner in doners)
        logger.debug("Budget is: %s" , budget)
        if not projects:
            return S
        eligible_projects = eligible_fn(doners, projects) # "If there are projects that are eligible for funding..."
        logger.debug("Eligible projects: %s" , [project.name for project in eligible_projects])
        
        for project in projects:
            donations = sum(doner[project.name] for doner in doners)
            logger.debug("Donors and total donations for %s: %s" , project.name, donations)
        
        while not eligible_projects:
            flag = no_eligible_project_procedure(doners, projects, eliminated_projects, project_to_fund_selection_procedure)
            if not flag:
                S = inclusive_maximality_postprocedure(doners, S, eliminated_projects, project_to_fund_selection_procedure, budget)
                logger.debug("Final selected projects: %s" , [project.name for project in S])
                return S
            eligible_projects = eligible_fn(doners, projects)

        p = project_to_fund_selection_procedure(doners, eligible_projects) # ...choose one such project p according to the “project-to-fund selection procedure”
        excess_support = sum(doner.get(p.name, 0) for doner in doners) - p.cost
        logger.debug("Excess support for %s: %s" , p.name, excess_support)

        if excess_support >= 0:
            if excess_support > 0:
                gama = p.cost / (excess_support + p.cost)
                projects = excess_redistribution_procedure(projects, p, doners, gama)
            else:
                logger.debug(f"Resetting donations for eliminated project: {p.name}")
                doners = [[0] * len(doner) for doner in doners]
            S.add(p)
            projects.remove(p)
            logger.debug("Updated selected projects: %s" , [project.name for project in S])
            budget -= p.cost
            continue



###################################################################
#                                                                 #
#                     Help functions                              #
#                                                                 #
###################################################################

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
    logger.debug(f"Resetting donations for eliminated project: {index}")
    for doner in doners:
        doner[index] = 0
    return doners

def check_equal_donations(donors: List[CumulativeBallot]) -> bool:
    """
    Checks if all donors donated the same amount.

    Parameters
    ----------
    donors : List[CumulativeBallot]
        The list of CumulativeBallot objects representing the donors.

    Returns
    -------
    bool
        True if all donations are the same, False otherwise.

    Examples
    --------
    >>> from pabutools.election import CumulativeBallot
    >>> donor1 = CumulativeBallot({"Project A": 10, "Project B": 10, "Project C": 0})
    >>> donor2 = CumulativeBallot({"Project A": 5, "Project B": 5, "Project C": 10})
    >>> donor3 = CumulativeBallot({"Project A": 0, "Project B": 0, "Project C": 20})
    >>> check_equal_donations([donor1, donor2, donor3])
    True
    >>> donor4 = CumulativeBallot({"Project A": 10, "Project B": 0, "Project C": 5})
    >>> check_equal_donations([donor1, donor2, donor4])
    False
    """
    if not donors:
        return True  # Consider an empty list as all donations being the same
    donation_amounts = [sum(donor.values()) for donor in donors]
    flag = len(set(donation_amounts)) == 1
    if flag:
        logger.debug("All the donations are equal")
    else:
        logger.debug("Some donations are not equal")
    return flag



def distribute_project_support(projects: Instance, eliminated_project: Project, doners: List[CumulativeBallot]) -> Instance:
    """
    Distributes the support of an eliminated project to the remaining projects.

    Parameters
    ----------
    projects : Instance
        The list of projects.
    eliminated_project : Project
        The project that has been eliminated.
    doners : List[CumulativeBallot]
        The list of doner ballots.

    Returns
    -------
    Instance
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0, "Project C": 5})
    >>> updated_projects = distribute_project_support(Instance[project_A, Project("Project B", 30), Project("Project C", 30)], project_A, [doner1, doner2])
    >>> updated_projects
    pabutools.election.instance.Instance[Project A, Project B, Project C]
    >>> for doner in [doner1, doner2]:
    ...     print({key: round(value, 2) for key, value in doner.items()})
    {'Project A': 0, 'Project B': 13.33, 'Project C': 6.67}
    {'Project A': 0, 'Project B': 0.0, 'Project C': 15.0}
    """
    
    eliminated_name = eliminated_project.name
    logger.debug(f"Distributing support of eliminated project: {eliminated_name}")
    for doner in doners:
        toDistribute = doner[eliminated_name]
        total = sum(doner.values())-toDistribute
        if total == 0:
            continue
        for key, donation in doner.items():
            if key != eliminated_name:
                part = donation / total
                doner[key] = donation + toDistribute * part
    doners = reset_donations(doners,eliminated_name)
    return projects

def excess_redistribution_procedure(projects: Instance, max_excess_project: Project, doners: List[CumulativeBallot], gama: float) -> Instance:
    """
    Distributes the excess support of a selected project to the remaining projects.

    Parameters
    ----------
    projects : Instance
        The list of projects.
    max_excess_project : Project
        The project with the maximum excess support.
    doners : List[CumulativeBallot]
        The list of doner ballots.
    gama : float
        The proportion to distribute.

    Returns
    -------
    Instance
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0, "Project C": 5})
    >>> updated_projects = excess_redistribution_procedure([project_A, project_B, project_C], project_A, [doner1, doner2], 0.5)
    >>> updated_projects
    [Project A, Project B, Project C]
    >>> for doner in [doner1, doner2]:
    ...     print({key: round(value, 2) for key, value in doner.items()})
    {'Project A': 0, 'Project B': 11.67, 'Project C': 5.83}
    {'Project A': 0, 'Project B': 0.0, 'Project C': 10.0}
    """
    max_project_name = max_excess_project.name
    logger.debug(f"Distributing excess support of selected project: {max_project_name}")
    for doner in doners:
        doner_copy = doner.copy()
        toDistribute = doner_copy[max_project_name] * (1 - gama)
        doner[max_project_name] = toDistribute
        doner_copy[max_project_name] = 0
        total = sum(doner_copy.values())
        for key, donation in doner_copy.items():
            if donation != max_project_name:
                if total != 0:
                    part = donation / total
                    doner[key] = donation + toDistribute * part
                    doner[max_project_name] = 0

    return projects



def is_eligible_GE(doners: List[CumulativeBallot], projects:Instance) -> Instance:
    """
    Determines the eligible projects based on the General Election (GE) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : Instance
        The list of projects.

    Returns
    -------
    Instance
        The list of eligible projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 30})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> is_eligible_GE([doner1, doner2], [project_A, project_B])
    [Project B]
    """
    return [project for project in projects if (sum(doner.get(project.name, 0) for doner in doners) - project.cost) >= 0]

def is_eligible_GSC(doners: List[CumulativeBallot], projects: Instance) -> Instance: 
    """
    Determines the eligible projects based on the Greatest Support to Cost (GSC) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : Instance
        The list of projects.

    Returns
    -------
    Instance
        The list of eligible projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 30, "Project B": 0})
    >>> is_eligible_GSC([doner1, doner2], [project_A, project_B])
    [Project A]
    """
    return [project for project in projects if (sum(doner.get(project.name, 0) for doner in doners) / project.cost) >= 1]



def select_project_GE(doners: List[CumulativeBallot], projects: Instance) -> Project:
    """
    Selects the project with the maximum excess support using the General Election (GE) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : Instance
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
    
    excess_support = {project: sum(doner.get(project.name, 0) for doner in doners) - project.cost for project in projects}
    max_excess_project = max(excess_support, key=excess_support.get)
    logger.debug(f"Selected project by GE method: {max_excess_project.name}")
    return max_excess_project

def select_project_GSC(doners: List[CumulativeBallot], projects: Instance) -> Project:
    """
    Selects the project with the maximum ratio of support to cost using the Greatest Support to Cost (GSC) rule.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : Instance
        The list of projects.

    Returns
    -------
    Project
        The selected project.

    Examples
    --------
    >>> project_A = Project("Project A", 34)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> select_project_GSC([doner1, doner2], [project_A, project_B]).name
    'Project A'
    """
    
    ratio_support = {project: sum(doner.get(project.name, 0) for doner in doners) / project.cost for project in projects}
    max_ratio_project = max(ratio_support, key=ratio_support.get)
    logger.debug(f"Selected project by GSC method: {max_ratio_project.name}")
    return max_ratio_project

def elimination_with_transfers(doners: List[CumulativeBallot], projects: Instance, eliminated_projects: Instance, _:callable) -> Instance:
    """
    Eliminates the project with the least excess support and redistributes its support to the remaining projects.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : Instance
        The list of projects.
    eliminated_projects : Instance
        The list of eliminated projects.
    _ : callable
        A placeholder for a callable function.

    Returns
    -------
    Instance
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 30)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 20)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0, "Project C": 5})
    >>> elimination_with_transfers([doner1, doner2], [project_A, project_B, project_C], [], None)
    True
    >>> print(doner1["Project A"])
    10.0
    >>> print(doner1["Project B"])
    0
    >>> print(doner2["Project A"])
    10.0
    >>> print(doner2["Project B"])
    0
    >>> print(doner1["Project C"])
    10.0
    >>> print(doner2["Project C"])
    5.0

    """
    
    if len(projects) < 2:
        logger.debug("Not enough projects to eliminate.")
        if len(projects) == 1:
            eliminated_projects.append(projects.pop())
        return False
    min_project = min(projects, key=lambda p: sum(doner.get(p.name, 0) for doner in doners) - p.cost)

    logger.debug(f"Eliminating project with least excess support: {min_project.name}")
    projects = distribute_project_support(projects, min_project, doners)
    projects.remove(min_project)
    eliminated_projects.append(min_project)
    return True

def minimal_transfer(doners: List[CumulativeBallot], projects: Instance, eliminated_projects: Instance, project_to_fund_selection_procedure:callable) -> Instance:
    """
    Performs minimal transfer of donations to reach the required support for a selected project.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    projects : Instance
        The list of projects.
    eliminated_projects : Instance
        The list of eliminated projects.
    project_to_fund_selection_procedure : callable
        The procedure to select a project for funding.

    Returns
    -------
    Instance
        The updated list of projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> minimal_transfer([doner1, doner2], [project_A, project_B], [], select_project_GE)
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
    logger.debug(f"Selected project for minimal transfer: {chosen_project.name}")
    r = sum(doner.get(chosen_project.name, 0) for doner in doners) / chosen_project.cost
    doners_of_selected_project = [doner for doner in doners if (doner.get(chosen_project.name, 0)) > 0]
    while r < 1:
        flag = True
        for doner in doners_of_selected_project:
            if sum(doner.values()) != doner.get(chosen_project.name, 0):
                flag = False
                break
        if flag:
            eliminated_projects.append(chosen_project)
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
        r = sum(doner.get(chosen_project.name, 0) for doner in doners) / chosen_project.cost
    return True

def reverse_eliminations(doners:List[CumulativeBallot], S: Instance, eliminated_projects: Instance, _:callable, budget: int) -> Instance:
    """
    Reverses eliminations of projects if the budget allows.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    selected_projects : Instance
        The list of selected projects.
    eliminated_projects : Instance
        The list of eliminated projects.
    _ : callable
        A placeholder for a callable function.
    budget : int
        The remaining budget.

    Returns
    -------
    Instance
        The updated list of selected projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> selected_projects = Instance([project_A])
    >>> eliminated_projects =  Instance([project_B])
    >>> len(reverse_eliminations([], selected_projects, eliminated_projects, None, 30))
    2
    """
    
    for project in eliminated_projects:
        if project.cost <= budget:
            S.add(project)
            budget -= project.cost
    return S

def acceptance_of_undersupported_projects(doners: List[CumulativeBallot], selected_projects: Instance, eliminated_projects:Instance, project_to_fund_selection_procedure: callable, budget: int) ->Instance:
    """
    Accepts undersupported projects if the budget allows.

    Parameters
    ----------
    doners : List[CumulativeBallot]
        The list of doner ballots.
    selected_projects : Instance
        The list of selected projects.
    eliminated_projects : Instance
        The list of eliminated projects.
    project_to_fund_selection_procedure : callable
        The procedure to select a project for funding.
    budget : int
        The remaining budget.

    Returns
    -------
    Instance
        The updated list of selected projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 20)
    >>> selected_projects = Instance(init=[project_A])
    >>> eliminated_projects = Instance(init=[project_B, project_C])
    >>> print(len(acceptance_of_undersupported_projects([], selected_projects, eliminated_projects, select_project_GE, 25)))
    2
    """
    while len(eliminated_projects) != 0:
        selected_project = project_to_fund_selection_procedure(doners, eliminated_projects)
        if selected_project.cost <= budget:
            selected_projects.add(selected_project)
            eliminated_projects.remove(selected_project)
            budget -= selected_project.cost
        else:
            eliminated_projects.remove(selected_project)
    return selected_projects



def cstv_budgeting_combination(doners: List[CumulativeBallot], projects: Instance, combination: str) -> Instance:
    """
    Runs the CSTV test based on the combination of functions provided.

    Parameters
    ----------
    combination : str
        The combination of CSTV functions to run.

    Returns
    -------
    Instance
        The selected projects.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 25)
    >>> instance = Instance([project_A, project_B, project_C])
    >>> doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> doner2 = CumulativeBallot({"Project A": 10, "Project B": 10, "Project C": 0})
    >>> doner3 = CumulativeBallot({"Project A": 0, "Project B": 15, "Project C": 5})
    >>> doner4 = CumulativeBallot({"Project A": 0, "Project B": 0, "Project C": 20})
    >>> doner5 = CumulativeBallot({"Project A": 15, "Project B": 5, "Project C": 0})
    >>> doners = [doner1, doner2, doner3, doner4, doner5]
    >>> combination = "ewt"
    >>> print(len(cstv_budgeting_combination(doners, instance, combination)))
    3
    """
    combination = combination.lower()
    if combination =="ewt":
        return cstv_budgeting(doners, projects, select_project_GE, is_eligible_GE, elimination_with_transfers, reverse_eliminations)
    elif combination =="ewtc":
        return cstv_budgeting(doners, projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
    elif combination =="mt":
        return cstv_budgeting(doners, projects, select_project_GE, is_eligible_GE, minimal_transfer, acceptance_of_undersupported_projects)
    elif combination =="mtc":
        return cstv_budgeting(doners, projects, select_project_GSC, is_eligible_GSC, minimal_transfer, acceptance_of_undersupported_projects)
    else:
        raise KeyError(f"Invalid combination algorithm: {combination}. Please insert an existing combination algorithm.")


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

    instance = Instance(init=[project_A, project_B, project_C, project_D])
    doners = [doner1, doner2, doner3, doner4, doner5]

    
    selected_projects = cstv_budgeting_combination(doners, instance,"ewt")
    if selected_projects:
        logger.info(f"Selected projects: {[project.name for project in selected_projects]}")



if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    main()
    import doctest
    doctest.testmod()

# ח. אפשר לקצר מאד חלק מהבדיקות, למשל ליצור את מערך הפרויקטים בשורה אחת. 
