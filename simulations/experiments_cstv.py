"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achiya Ben Natan
Date: 2024/05/16.
"""

import random
import time
import logging
from pabutools.rules.cstv import *
import matplotlib.pyplot as plt
import copy
from experiments_csv import Experiment

def old_minimal_transfer(projects: Instance, donors: list[CumulativeBallot], eliminated_projects: Instance, project_to_fund_selection_procedure:callable) -> Instance:
    chosen_project = project_to_fund_selection_procedure(projects, donors)
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

def improved_minimal_transfer(projects: Instance, donors: list[CumulativeBallot],  eliminated_projects: Instance, project_to_fund_selection_procedure: callable) -> bool:
    chosen_project = project_to_fund_selection_procedure(projects,donors)
    # 1. Simplified and descriptive variable names
    project_name = chosen_project.name
    project_cost = chosen_project.cost
    # 2. Clear initial support calculation
    total_support = sum(donor.get(project_name, 0) for donor in donors)
    r = total_support / project_cost

    # 3. Efficient donor selection using list comprehension
    donors_of_selected_project = [i for i, donor in enumerate(donors) if donor.get(project_name, 0) > 0]

    # 4. Loop focused on achieving required support
    while r < 1:
        # 5. Concise check if all donors are fully allocated to the chosen project instead of checking one by one.
        all_on_chosen_project = all(
            float(Decimal(str(sum(donors[i].values()))).quantize(Decimal('1e-5'))) ==
            float(Decimal(str(donors[i].get(project_name, 0))).quantize(Decimal('1e-5')))
            for i in donors_of_selected_project
        )

        if all_on_chosen_project:
            eliminated_projects.add(chosen_project)
            return False

        for i in donors_of_selected_project:
            donor = donors[i]
            total = sum(donor.values()) - donor.get(project_name, 0)
            donation = donor.get(project_name, 0)

            if total > 0:
                to_distribute = min(total, donation / r - donation)
                for proj_name, proj_donation in donor.items():
                    if proj_name != project_name and proj_donation > 0:
                        change = to_distribute * proj_donation / total
                        donor[proj_name] -= change
                        donor[project_name] += float(Decimal(str(change)).quantize(Decimal('1e-14'), rounding=ROUND_UP))

        total_support = sum(donor.get(project_name, 0) for donor in donors)
        r = total_support / project_cost

    return True

def cstv_budgeting_combination_exp(projects: Instance, donors: list[CumulativeBallot], combination: str) -> dict[str, Instance]:
    projects = copy.deepcopy(projects)
    donors = copy.deepcopy(donors)
    combination = combination.lower()
    if combination == "ewt":
        result = cstv_budgeting(projects, donors, select_project_GE, is_eligible_GE, elimination_with_transfers, reverse_eliminations)
    elif combination == "improved_mt":
        result = cstv_budgeting(projects, donors, select_project_GE, is_eligible_GE, improved_minimal_transfer, acceptance_of_undersupported_projects)
    elif combination == "old_mt":
        result = cstv_budgeting(projects, donors, select_project_GE, is_eligible_GE, old_minimal_transfer, acceptance_of_undersupported_projects)
    else:
        raise KeyError(f"Invalid combination algorithm: {combination}. Please insert an existing combination algorithm.")
    
    return {combination: result}

def exp_time():
    initial_num_projects = 100
    max_num_projects = 1000
    step = 100
    
    ex = Experiment("simulations/results","results.csv","simulations/backup_results")
    ex.logger.setLevel(logging.CRITICAL)
    ex.clear_previous_results()

    def generate_donations(total, num_projects):
        donations = [0] * num_projects
        for _ in range(total):
            donations[random.randint(0, num_projects - 1)] += 1
        return donations

    timings = { "ewt": [],  "improved_mt": [], "old_mt": [] }
    project_counts = list(range(initial_num_projects, max_num_projects + 1, step))

    for num_projects in project_counts:
        projects = Instance([Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)])
        donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(300, num_projects))}) for _ in range(int(num_projects))]
        donorsl = [donors]
        projectsl = [projects]
        input_ranges = {
            "donors": donorsl,
            "projects": projectsl,
            "combination": ["ewt", "improved_mt", "old_mt"]
        }

        for combination in input_ranges['combination']:
            print(combination)
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

def exp_with_variations():
    initial_num_projects = 500
    step = 100
    max_projects = 1000

    ex = Experiment("simulations/results", "results.csv", "simulations/backup_results")
    ex.logger.setLevel(logging.CRITICAL)
    ex.clear_previous_results()

    def generate_donations(total, num_projects):
        donations = [0] * num_projects
        for _ in range(total):
            donations[random.randint(0, num_projects - 1)] += 1
        return donations

    variations = [
        {"num_donors": 50, "total_donations": 300},
        {"num_donors": 100, "total_donations": 600},
        {"num_donors": 150, "total_donations": 900}
    ]

    for variation in variations:
        num_donors = variation["num_donors"]
        total_donations = variation["total_donations"]

        timings = {"ewt": [], "improved_mt": [], "old_mt": []}
        combinations = ["ewt", "improved_mt", "old_mt"]

        num_projects = initial_num_projects
        while num_projects <= max_projects:
            projects = Instance([Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)])
            donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(total_donations, num_projects))}) for _ in range(num_donors)]

            donorsl = [donors]
            projectsl = [projects]

            for combination in combinations:
                start_time = time.time()
                ex.run(cstv_budgeting_combination_exp, {"donors": donorsl, "projects": projectsl, "combination": [combination]})
                end_time = time.time()
                duration = end_time - start_time

                timings[combination].append(duration)

            num_projects += step        

        # Plotting the results for the current variation
        project_ranges = list(range(initial_num_projects, initial_num_projects + len(timings["ewt"]) * step, step))
        for combination, times in timings.items():
            plt.plot(project_ranges[:len(times)], times, label=f"{combination}")

        plt.xlabel("Number of Projects")
        plt.ylabel("Time (seconds)")
        plt.title(f"Time Taken for Different Combinations with Increasing Projects\nVariation: {variation}")
        plt.legend()
        plt.grid(True)
        plt.show()

# Run the experiments
logging.basicConfig(level=logging.INFO)
exp_time()
exp_with_variations()