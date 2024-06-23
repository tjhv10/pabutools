"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achia Ben Natan
Date: 2024/05/16.
"""

import random
import time
import logging
from pabutools.rules.CSTV import *
import matplotlib.pyplot as plt
import copy

from experiments_csv import Experiment

def old_minimal_transfer(donors: List[CumulativeBallot], projects: Instance, eliminated_projects: Instance, project_to_fund_selection_procedure:callable) -> Instance:
    """
    Performs minimal transfer of donations to reach the required support for a selected project.

    Parameters
    ----------
    donors : List[CumulativeBallot]
        The list of donor ballots.
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
    >>> donor1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> donor2 = CumulativeBallot({"Project A": 10, "Project B": 0})
    >>> minimal_transfer([donor1, donor2], [project_A, project_B], Instance([]), select_project_GE)
    False
    >>> print(donor1["Project A"])
    15.00000000000001
    >>> print(donor1["Project B"])
    0.0
    >>> print(donor2["Project A"])
    10
    >>> print(donor2["Project B"])
    0
    """
    chosen_project = project_to_fund_selection_procedure(donors, projects)
    logger.debug(f"Selected project for minimal transfer: {chosen_project.name}")
    r = sum(donor.get(chosen_project.name, 0) for donor in donors) / chosen_project.cost
    donors_of_selected_project = [donor for donor in donors if (donor.get(chosen_project.name, 0)) > 0]
    while r < 1:
        flag = True
        for donor in donors_of_selected_project:
            if float(Decimal(str(sum(donor.values()))).quantize(Decimal('1e-'+str(5)))) != float(Decimal(str(donor.get(chosen_project))).quantize(Decimal('1e-'+str(5)))):
                flag = False
                break
        if flag:
            eliminated_projects.add(chosen_project)
            return False
        for donor in donors_of_selected_project:
            total = sum(donor.values()) - donor.get(chosen_project.name)
            donation = donor.get(chosen_project.name)
            to_distribute = min(total, donation / r - donation)
            for project_name, donation in donor.items():
                if project_name != chosen_project.name and total > 0:
                    change = to_distribute * donation / total
                    donor[project_name] -= change
                    donor[chosen_project.name] += float(Decimal(str(change)).quantize(Decimal('1e-'+str(14)), rounding=ROUND_UP))
        r = sum(donor.get(chosen_project.name, 0) for donor in donors) / chosen_project.cost
    return True


def cstv_budgeting_combination_exp(donors: List[CumulativeBallot], projects: Instance, combination: str) -> dict[str, Instance]:
    """
    Runs the CSTV test based on the combination of functions provided.

    Parameters
    ----------
    combination : str
        The combination of CSTV functions to run.

    Returns
    -------
    dict[str, Instance]
        The selected projects as a dictionary with the combination name as the key.

    Examples
    --------
    >>> project_A = Project("Project A", 35)
    >>> project_B = Project("Project B", 30)
    >>> project_C = Project("Project C", 25)
    >>> instance = Instance([project_A, project_B, project_C])
    >>> donor1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5})
    >>> donor2 = CumulativeBallot({"Project A": 10, "Project B": 10, "Project C": 0})
    >>> donor3 = CumulativeBallot({"Project A": 0, "Project B": 15, "Project C": 5})
    >>> donor4 = CumulativeBallot({"Project A": 0, "Project B": 0, "Project C": 20})
    >>> donor5 = CumulativeBallot({"Project A": 15, "Project B": 5, "Project C": 0})
    >>> donors = [donor1, donor2, donor3, donor4, donor5]
    >>> combination = "ewt"
    >>> print(len(cstv_budgeting_combination_exp(donors, instance, combination)))
    1
    """
    projects = copy.deepcopy(projects)
    donors = copy.deepcopy(donors)
    combination = combination.lower()
    if combination == "ewt":
        result = cstv_budgeting(donors, projects, select_project_GE, is_eligible_GE, elimination_with_transfers, reverse_eliminations)
    elif combination == "mt":
        result = cstv_budgeting(donors, projects, select_project_GE, is_eligible_GE, minimal_transfer, acceptance_of_undersupported_projects)
    elif combination == "old_mt":
        result = cstv_budgeting(donors, projects, select_project_GE, is_eligible_GE, old_minimal_transfer, acceptance_of_undersupported_projects)
    else:
        raise KeyError(f"Invalid combination algorithm: {combination}. Please insert an existing combination algorithm.")
    
    return {combination: result}

def exp():
    initial_num_projects = 100
    max_num_projects = 5000
    step = 100
    
    ex = Experiment("simulations/results","results.csv","simulations/backup_results")
    ex.logger.setLevel(logging.CRITICAL)
    ex.clear_previous_results()

    def generate_donations(total, num_projects):
        donations = [0] * num_projects
        for _ in range(total):
            donations[random.randint(0, num_projects - 1)] += 1
        return donations

    timings = { "ewt": [],  "mt": [], "old_mt": [] }
    project_counts = list(range(initial_num_projects, max_num_projects + 1, step))

    for num_projects in project_counts:
        projects = Instance([Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)])
        donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(300, num_projects))}) for _ in range(num_projects)]
        
        donorsl = [donors]
        projectsl = [projects]
        input_ranges = {
            "donors": donorsl,
            "projects": projectsl,
            "combination": ["ewt", "mt", "old_mt"]
        }

        for combination in input_ranges['combination']:
            start_time = time.time()
            ex.run(cstv_budgeting_combination_exp, {"donors": donorsl, "projects": projectsl, "combination": [combination]})
            end_time = time.time()
            duration = end_time - start_time
            timings[combination].append(duration)
            

    # Plotting the results
    for combination, times in timings.items():
        plt.plot(project_counts, times, label=f"{combination}")

    plt.xlabel("Number of Projects")
    plt.ylabel("Time (seconds)")
    plt.title("Time Taken for Different Combinations with Increasing Projects")
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the experiment
logging.basicConfig(level=logging.CRITICAL)
exp()
