# # # import experiments_csv as ecsv

# # # manager = ecsv.ExperimentManager('experiments.csv')





# # from typing import List
# # from pabutools.rules.CSTV import *


# # # Assume the classes and functions from previous code are defined here

# # def load_experiment_data():
# #     num_projects = 10
# #     projects = [Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)]
# #     # Function to generate a list of donations that sum to total_donation
# #     def generate_donations(total, num_projects):
# #         donations = [0] * num_projects
# #         for _ in range(total):
# #             donations[random.randint(0, num_projects - 1)] += 1
# #         return donations

# #     # Generate the donations for each donor
# #     donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(300, num_projects))})for _ in range(num_projects)]
# #     return projects,donors

# # def run_experiment(csv_file: str, combinations: List[str]):
# #     for combination in combinations:
# #         projects, donors = load_experiment_data()
# #         print(f"Testing combination: {combination}")
# #         selected_projects = cstv_budgeting_combination(donors, projects, combination)
# #         print(f"Selected projects for combination '{combination}':")
# #         for project in selected_projects:
# #             print(f"{project.name} with cost {project.cost}")
# #         print("-" * 40)

# # # Example usage
# # csv_file = 'simulations\experiments.csv'  # Replace with the actual path to the CSV file
# # combinations = ["ewt", "ewtc", "mt", "mtc"]
# # run_experiment(csv_file, combinations)





# import random
# import csv
# from typing import List, Dict, Any
# from pabutools.rules.CSTV import *
# import experiments_csv as ecsv

# # Assuming Project and CumulativeBallot classes are defined as in previous snippets

# # Function to generate projects and donors for the experiment
# def load_experiment_data():
#     num_projects = 10
#     projects = [Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)]
#     # Function to generate a list of donations that sum to total_donation
#     def generate_donations(total, num_projects):
#         donations = [0] * num_projects
#         for _ in range(total):
#             donations[random.randint(0, num_projects - 1)] += 1
#         return donations

#     # Generate the donations for each donor
#     donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(300, num_projects))})for _ in range(num_projects)]
#     return projects,donors

# # Function to load experiments from CSV
# def load_experiments_from_csv(csv_file: str) -> List[Dict[str, Any]]:
#     experiments = []
#     with open(csv_file, mode='r') as file:
#         csv_reader = csv.DictReader(file)
#         for row in csv_reader:
#             experiments.append(row)
#     return experiments

# # Function to run the experiment
# def run_experiment(csv_file: str):
#     experiments = load_experiment_data()
#     print(experiments)
#     for experiment in experiments:
#         combination = experiment['combination']
#         num_projects = int(experiment['num_projects'])
#         total_donation = int(experiment['total_donation'])
        
#         projects, donors = load_experiment_data(num_projects, total_donation)
        
#         print(f"Testing combination: {combination}")
#         selected_projects = cstv_budgeting_combination(donors, projects, combination)
        
#         print(f"Selected projects for combination '{combination}':")
#         for project in selected_projects.projects:
#             print(f"{project.name} with cost {project.cost}")
        
#         print("-" * 40)

# # Example usage
# csv_file = 'simulations/experiments.csv'
# run_experiment(csv_file)
