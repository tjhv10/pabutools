import random
import time
import logging
import matplotlib.pyplot as plt
from pabutools.rules.CSTV import *
from experiments_csv import Experiment

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
    elif combination == "ewtc":
        result = cstv_budgeting(donors, projects, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations)
    elif combination == "mt":
        result = cstv_budgeting(donors, projects, select_project_GE, is_eligible_GE, minimal_transfer, acceptance_of_undersupported_projects)
    elif combination == "mtc":
        result = cstv_budgeting(donors, projects, select_project_GSC, is_eligible_GSC, minimal_transfer, acceptance_of_undersupported_projects)
    else:
        raise KeyError(f"Invalid combination algorithm: {combination}. Please insert an existing combination algorithm.")
    
    return {combination: result}

def exp():
    initial_num_projects = 100
    max_num_projects = 400
    step = 100
    
    ex = Experiment("simulations/results","results.csv","simulations/backup_results")
    ex.logger.setLevel(logging.CRITICAL)
    ex.clear_previous_results()

    def generate_donations(total, num_projects):
        donations = [0] * num_projects
        for _ in range(total):
            donations[random.randint(0, num_projects - 1)] += 1
        return donations

    timings = { "ewt": [], "ewtc": [], "mt": [], "mtc": [] }
    project_counts = list(range(initial_num_projects, max_num_projects + 1, step))

    for num_projects in project_counts:
        projects = Instance([Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)])
        donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(300, num_projects))}) for _ in range(num_projects)]
        
        donorsl = [donors]
        projectsl = [projects]
        input_ranges = {
            "donors": donorsl,
            "projects": projectsl,
            "combination": ["ewt", "ewtc", "mt", "mtc"]
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
exp()
