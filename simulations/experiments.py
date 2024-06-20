import random
import time
import logging
import matplotlib.pyplot as plt
from pabutools.rules.CSTV import *
from experiments_csv import Experiment


def exp():
    initial_num_projects = 10
    max_num_projects = 40
    step = 10
    
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
            ex.run(cstv_budgeting_combination, {"donors": donorsl, "projects": projectsl, "combination": [combination]})
            end_time = time.time()
            duration = end_time - start_time
            timings[combination].append(duration)
            # eligible_projects_count = extract_selected_projects_count(result.__str__())
            logging.info(f"Combination {combination} with {num_projects} projects took {duration:.4f} seconds and found {eligible_projects_count} projects that are eligible for funding.")
            

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
