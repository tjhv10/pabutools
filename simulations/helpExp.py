import random
import time
from pabutools.rules.cstv import *
import copy
from experiments_csv import *



def old_minimal_transfer(projects: Instance, donors: list[CumulativeBallot], eliminated_projects: Instance, project_to_fund_selection_procedure:callable, tie_breaking: TieBreakingRule) -> Instance:
    projects_with_chance = []
    for project in projects:
        donors_of_selected_project = [donor.values() for _, donor in enumerate(donors) if donor.get(project.name, 0) > 0]
        sum_of_don = 0
        for d in donors_of_selected_project:
            sum_of_don+= sum(d)
        if sum_of_don >= project.cost:
            projects_with_chance.append(project)
    if not projects_with_chance:
        return False
    chosen_project = project_to_fund_selection_procedure(projects_with_chance, donors,tie_breaking)
    r = sum(donor.get(chosen_project.name, 0) for donor in donors) / chosen_project.cost
    donors_of_selected_project = [donor for donor in donors if (donor.get(chosen_project.name, 0)) > 0]
    while r < 1:
        flag = True
        for donor in donors_of_selected_project:
            if sum(donor.values())!= donor.get(chosen_project):
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
                    donor[chosen_project.name] += np.ceil(change * 100000000000000) / 100000000000000
        r = sum(donor.get(chosen_project.name, 0) for donor in donors) / chosen_project.cost
    return True

def improved_minimal_transfer(projects: Instance, donors: Profile, eliminated_projects: Instance, project_to_fund_selection_procedure: callable, tie_breaking: TieBreakingRule) -> bool:
    """
    Performs minimal transfer of donations to reach the required support for a selected project.

    Parameters
    ----------
    donors : Profile
        The list of donor ballots.
    projects : Instance
        The list of projects.
    eliminated_projects : Instance
        The list of eliminated projects.
    project_to_fund_selection_procedure : callable
        The procedure to select a project for funding.

    Returns
    -------
    bool
        True if the minimal transfer was successful, False if the project was added to eliminated_projects.

    Examples
    --------
    >>> project_A = Project("Project A", 40)
    >>> project_B = Project("Project B", 30)
    >>> donor1 = CumulativeBallot({"Project A": 5, "Project B": 10})
    >>> donor2 = CumulativeBallot({"Project A": 30, "Project B": 0})
    >>> minimal_transfer([project_A, project_B], [donor1, donor2], Instance([]), select_project_GE,lexico_tie_breaking)
    True
    >>> print(donor1["Project A"])
    9.999999999999996
    >>> print(donor1["Project B"])
    5.000000000000034
    >>> print(donor2["Project A"])
    30
    >>> print(donor2["Project B"])
    0
    """
    
    projects_with_chance = []
    for project in projects:
        donors_of_selected_project = [donor.values() for _, donor in enumerate(donors) if donor.get(project.name, 0) > 0]
        sum_of_don = 0
        for d in donors_of_selected_project:
            sum_of_don+= sum(d)
        if sum_of_don >= project.cost:
            projects_with_chance.append(project)
    if not projects_with_chance:
        return False
    chosen_project = project_to_fund_selection_procedure(projects_with_chance, donors,tie_breaking)
    donors_of_selected_project = [i for i, donor in enumerate(donors) if donor.get(chosen_project.name, 0) > 0]
    logger.debug(f"Selected project for minimal transfer: {chosen_project.name}")

    project_name = chosen_project.name
    project_cost = chosen_project.cost

    # Calculate initial support ratio
    total_support = sum(donor.get(project_name, 0) for donor in donors)
    r = total_support / project_cost

    # Loop until the required support is achieved
    while r < 1:
        # Check if all donors have their entire donation on the chosen project
        all_on_chosen_project = all(
            sum(donors[i].values()) == donors[i].get(project_name, 0) for i in donors_of_selected_project)

        if all_on_chosen_project:
            for project in projects:
                eliminated_projects.add(copy.deepcopy(project))
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
                        donor[project_name] += np.ceil(change * 100000000000) / 100000000000

        # Recalculate the support ratio
        total_support = sum(donor.get(project_name, 0) for donor in donors)
        r = total_support / project_cost
    return True

def cstv_budgeting_combination_exp(inputs, combination: str,para = False) -> dict[str, BudgetAllocation]:
    
    
    combination = combination.lower()
    projects = copy.deepcopy(inputs[0])
    donors = copy.deepcopy(inputs[1])
    start_time = time.time()
    if combination == "ewt":
        results = cstv_budgeting(projects, donors, select_project_GE, is_eligible_GE, elimination_with_transfers, reverse_eliminations, lexico_tie_breaking)
    elif combination == "improved_mt":
        results = cstv_budgeting(projects, donors, select_project_GE, is_eligible_GE, improved_minimal_transfer, acceptance_of_undersupported_projects, lexico_tie_breaking)
    elif combination == "old_mt":
        results = cstv_budgeting(projects, donors, select_project_GE, is_eligible_GE, old_minimal_transfer, acceptance_of_undersupported_projects, lexico_tie_breaking)
    elif combination == "ewtc":
        results = cstv_budgeting(projects, donors, select_project_GSC, is_eligible_GSC, elimination_with_transfers, reverse_eliminations, lexico_tie_breaking)
    elif combination == "old_mtc":
        results = cstv_budgeting(projects, donors, select_project_GSC, is_eligible_GSC, old_minimal_transfer, acceptance_of_undersupported_projects, lexico_tie_breaking)
    elif combination == "improved_mtc":
        results = cstv_budgeting(projects, donors, select_project_GSC, is_eligible_GSC, improved_minimal_transfer, acceptance_of_undersupported_projects, lexico_tie_breaking)
    else:
        raise KeyError(f"Invalid combination algorithm: {combination}. Please insert an existing combination algorithm.")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"{combination} executed in {elapsed_time:.2f} seconds")
    if para:
        return {"results": results}
    return {"time_taken": elapsed_time}


def create_inputs_2():
    initial_num_projects = 300
    step = 100
    max_projects = 500

    
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

        num_projects = initial_num_projects
        inputs = []
        while num_projects <= max_projects:
            projects = Instance([Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)])
            donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(total_donations, num_projects))}) for _ in range(num_donors)]
            inputs.append((projects,donors))
            num_projects += step
    
    return inputs


def create_input_1():
    initial_num_projects = 100
    max_num_projects = 300
    step = 100
    
    def generate_donations(total, num_projects):
        donations = [0] * num_projects
        for _ in range(total):
            donations[random.randint(0, num_projects - 1)] += 1
        return donations

    project_counts = list(range(initial_num_projects, max_num_projects + 1, step))
    inputs = []
    for num_projects in project_counts:
        projects = Instance([Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)])
        donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(300, num_projects))}) for _ in range(int(num_projects))]
        inputs.append((projects,donors))
    return inputs

def create_input_3():
    def generate_donations(total, num_projects):
        donations = [0] * num_projects
        for _ in range(total):
            donations[random.randint(0, num_projects - 1)] += 1
        return donations

    num_projects = 100
    projects = Instance([Project(f"Project_{i}", random.randint(100, 1000)) for i in range(num_projects)])
    donors = [CumulativeBallot({f"Project_{i}": donation for i, donation in enumerate(generate_donations(300, num_projects))}) for _ in range(num_projects)]
    
    return projects, donors


def calculate_metrics(inputs, combination):
    donors = inputs[1]
    selected_projects = cstv_budgeting_combination_exp(inputs,combination,True)
    total_voters = len(donors)
    # print(total_voters)
    key = next(iter(selected_projects))
    funded_projects = {project for project in selected_projects[key]}
    voter_satisfaction = []
    ignored_voters = 0
    for donor in donors:
        support = sum(donor.get(project, 0) for project in funded_projects)
        total_support = sum(donor.values())
        voter_satisfaction.append(support / total_support)
        if support == 0:
            ignored_voters += 1
    vs = sum(voter_satisfaction) / total_voters
    ar = ignored_voters / total_voters
    ac = sum(project.cost for project in selected_projects[key]) / len(selected_projects[key])
    return {"Voter Satisfaction | Anger Ratio | Average Cost":(vs, ar, ac)}







# def add(self, new_row:dict):
#         def extract_number_of_projects(data: dict) -> int:
#         # Extract the string containing project details
#             project_details = data['inputs'][0]

#             # Use regular expressions to find all occurrences of 'Project_' followed by a number
#             project_names = re.findall(r'Project_\d+', str(project_details))

#             # Use a set to find unique project names and get the count
#             unique_projects = set(project_names)
#             number_of_projects = len(unique_projects)
        
#             return number_of_projects
#         """
#         Add a data-row whose values exactly match the columns in self.columns.
#         """
#         if self.dataFrame is None:
#             columns = list(new_row.keys())
#             logger.debug("    Inserting first row: setting columns to %s", columns)
#             self.dataFrame = pandas.DataFrame(columns=columns)
#         index_of_new_row = self.dataFrame.shape[0]
        
#         new_row['inputs'] = "Projects num: "+str(extract_number_of_projects(new_row))
        
#         self.dataFrame.loc[index_of_new_row] = pandas.Series(new_row)
#         # self.dataFrame.iloc[index_of_new_row] = pandas.Series(dataRow) # IndexError: single positional indexer is out-of-bounds
#         # self.dataFrame = self.dataFrame.append(pandas.Series(dataRow), ignore_index=True) # This is inefficient! It creates and returns a new dataFrame.
#         self.to_csv(self.results_file)