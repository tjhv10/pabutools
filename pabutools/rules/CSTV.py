import logging
from pabutools.election import Project, CumulativeBallot
from typing import List

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def reset_donations(doners: List[CumulativeBallot], index: str) -> List[CumulativeBallot]:
    for doner in doners:
        doner[index] = 0
    return doners

def get_project_names(projects: List[Project]) -> List[str]:
    return [project.name for project in projects]

def distribute_project_support(projects: List[Project], eliminated_project: Project, doners: List[CumulativeBallot], listNames: List[str]) -> List[Project]:
    elimineited_name = eliminated_project.name
    for doner in doners:
        toDistribute = doner[eliminated_project.name]
        total = sum(doner.values())
        if total == 0:
            continue
        for i, donation in enumerate(doner.values()):
            if listNames[i] != elimineited_name:
                part = donation / total
                doner[listNames[i]] = donation + toDistribute * part
    doners = reset_donations(doners, elimineited_name)
    return projects

def elimination_with_transfers(projects: List[Project], doners: List[CumulativeBallot], listNames: List[str], eliminated_projects: List[Project]) -> List[Project]:
    if len(projects) < 2:
        return projects
    
    while projects:
        min_project = min(projects, key=lambda p: calculate_excess_support(doners,p))
        excess = calculate_excess_support(doners,min_project)

        if excess < 0:
            projects = distribute_project_support(projects, min_project, doners, listNames)
            projects.remove(min_project)
            eliminated_projects.append(min_project)
            break

    return projects


def minimal_transfer(doners: List[CumulativeBallot], projects: List[Project], listNames, eliminated_projects, project_to_fund_selection_procedure: callable) -> List[Project]:
    chosen_project = project_to_fund_selection_procedure(doners,projects)
    r = calculate_total_support_for_project(doners, chosen_project)/chosen_project.cost
    doners_of_selected_project = [doner for doner in doners if (doner.get(chosen_project.name,0)) > 0]
    while r<1:
        for doner in doners_of_selected_project:
            total = sum(doner.values()) - doner.get(chosen_project.name,0)
            to_distibute = min(sum(doner.values()),doner.get(chosen_project.name)/r)
            for project_name, donation in doner.items():
                if project_name !=chosen_project.name:
                    part = donation / total
                    change = to_distibute * part
                    doner[project_name]-=change
                    doner[chosen_project.name]+=change
        r = calculate_total_support_for_project(doners, chosen_project)/chosen_project.cost

def calculate_total_support_for_project(doners: List[CumulativeBallot], project: Project) -> float:
    total_support = sum(doner.get(project, 0) for doner in doners)
    return total_support


def calculate_total_initial_support(doners: List[CumulativeBallot], projects: List[Project]) -> int:
    return sum(calculate_total_support_for_project(doners,project) for project in projects)

def calculate_total_initial_support_doners(doners: List[CumulativeBallot]) -> int:
    return sum(sum(doner.values()) for doner in doners)

def calculate_excess_support(doners, project: Project) -> int:
    return calculate_total_support_for_project(doners,project) - project.cost

def select_project_GE(doners: List[CumulativeBallot],projects: List[Project]) -> Project:
    excess_support = {project: calculate_excess_support(doners,project) for project in projects}
    max_excess_project = max(excess_support, key=excess_support.get)
    return max_excess_project

def distribute_excess_support(projects: List[Project], max_excess_project: Project, doners: List[CumulativeBallot], gama: float, listNames: List[str]) -> List[Project]:
    max_project_name = max_excess_project.name
    for doner in doners:
        doner_copy = doner.copy()
        toDistribute = doner_copy[max_project_name] * (1 - gama)
        doner[max_project_name] = 0
        total = sum(doner_copy.values())
        for i, donation in enumerate(doner_copy.values()):
            if listNames[i] != max_project_name:
                if total != 0:
                    part = donation/total
                    doner[listNames[i]] = donation + toDistribute * part
    return projects

def select_project_GSC(doners: List[CumulativeBallot] ,project: Project) -> float:
    return (calculate_total_support_for_project(doners,project) / project.cost)

def find_project_index(listNames: List[str], name: str) -> int:
    return listNames.index(name)

def reverse_eliminations(selected_projects: List[Project], eliminated_projects: List[Project],project_to_fund_selection_procedure, budget: int) -> List[Project]:
    for project in reversed(eliminated_projects):
        if project.cost <= budget:
            selected_projects.append(project)
            budget -= project.get_cost()
    return selected_projects


def acceptance_of_undersupported_projects(selected_projects: List[Project], eliminated_projects: List[Project],project_to_fund_selection_procedure: callable, budget: int) -> List[Project]:
    while len(eliminated_projects)!=0:
        selected_project = project_to_fund_selection_procedure(eliminated_projects)
        if selected_project.cost<budget:
            selected_projects.append(selected_project)
            selected_projects.remove(selected_project)
            budget -= selected_project.get_cost()


def is_eligible_GE(doners: List[CumulativeBallot], projects: List[Project])-> List[Project]:
    return [project for project in projects if (calculate_total_support_for_project(doners,project) - project.cost) >= 0]

def is_eligible_GSC(doners: List[CumulativeBallot], projects: List[Project])-> List[Project]: 
    return [project for project in projects if (calculate_total_support_for_project(doners,project) / project.cost) >= 1]

def cstv_budgeting(doners: List[CumulativeBallot],projects: List[Project], project_to_fund_selection_procedure: callable, eligible_fn: callable,
                    no_eligible_project_procedure: callable, inclusive_maximality_postprocedure: callable) -> List[Project]:
    selected_projects = []
    eliminated_projects = []
    budget = calculate_total_initial_support_doners(doners)
    listNames = get_project_names(projects)

    while True:
        eligible_projects = eligible_fn(doners,projects)
        while not eligible_projects:
            pLength = len(projects)
            if pLength == 1:
                eliminated_projects.append(projects[-1])
            no_eligible_project_procedure(doners, projects, listNames, eliminated_projects,project_to_fund_selection_procedure)
            if len(projects) == pLength:
                selected_projects = inclusive_maximality_postprocedure(selected_projects, eliminated_projects,project_to_fund_selection_procedure, budget)
                return selected_projects
            eligible_projects = eligible_fn(doners,projects)

        selected_project = project_to_fund_selection_procedure(doners,eligible_projects)
        excess_support = calculate_excess_support(doners,selected_project)

        if excess_support >= 0:
            selected_projects.append(selected_project)
            if excess_support > 0:
                gama = selected_project.cost / (excess_support + selected_project.cost)
                projects = distribute_excess_support(projects, selected_project, doners, gama, listNames)
            projects.remove(selected_project)
            budget -= selected_project.cost
            continue

def main():
    project_A = Project("Project A", 35)
    project_B = Project("Project B", 30)
    project_C = Project("Project C", 35)
    project_D = Project("Project D", 30)
    
    doner1 = CumulativeBallot({"Project A": 5, "Project B": 10, "Project C": 5, "Project D": 5})
    doner2 = CumulativeBallot({"Project A": 10, "Project B": 10, "Project C": 0, "Project D": 5})
    doner3 = CumulativeBallot({"Project A": 0, "Project B": 15, "Project C": 5, "Project D": 5})
    doner4 = CumulativeBallot({"Project A": 0, "Project B": 0, "Project C": 20, "Project D": 5})
    doner5 = CumulativeBallot({"Project A": 15, "Project B": 5, "Project C": 0, "Project D": 5})

    projects = [project_A, project_B, project_C, project_D]
    doners = [doner1, doner2, doner3, doner4, doner5]
    project_to_fund_selection_procedure = select_project_GE
    eligible_fn = is_eligible_GE
    no_eligible_project_procedure = minimal_transfer
    inclusive_maximality_postprocedure = acceptance_of_undersupported_projects
    selected_projects = cstv_budgeting(
        doners,
        projects,
        project_to_fund_selection_procedure,
        eligible_fn,
        no_eligible_project_procedure,
        inclusive_maximality_postprocedure
    )

    for project in selected_projects:
        logging.info(f"Selected Project: {project.name}")

if __name__ == "__main__":
    main()
