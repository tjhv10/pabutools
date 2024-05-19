
"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achia Ben Natan
Date: 2024/05/16.
"""

class Project:
    """
    Represents a project with a name, cost, and support.

    Parameters
    ----------
        name : str
            The name of the project.
        cost : Numeric
            The cost of the project.

    Attributes
    ----------
        name : str
            The name of the project.
        cost : Numeric
            The cost of the project.
        support : list
            A list of support' contributions.

    Methods
    -------
        update_support(supporter)
            Updates a supporter's contribution to the project.
        get_name()
            Returns the name of the project.
        get_cost()
            Returns the cost of the project.
        __str__()
            Returns a string representation of the project.
    """

    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.support = []

    def update_support(self, support):
        """
        Updates a supporter's contribution to the project.

        Parameters
        ----------
            supporter : list
                List of supporter contributions.
        """
        self.support = support

    def get_name(self):
        """
        Returns the name of the project.
        """
        return self.name

    def get_cost(self):
        """
        Returns the cost of the project.
        """
        return self.cost

    def __str__(self):
        """
        Returns a string representation of the project.
        """
        supporter_strings = ", ".join(str(s) for s in self.support)
        return f"Project: {self.name}, Cost: {self.cost}, Initial support: [{supporter_strings} sum:{sum(self.support)}]"


class Doner:
    """
    Represents a doner with donations.

    Parameters
    ----------
        donations : list
            A list of donations made by the doner.

    Methods
    -------
        get_donations()
            Returns the list of donations made by the doner.
    """

    def __init__(self, donations):
        self.donations = donations

    def get_donations(self):
        """
        Returns the list of donations made by the doner.
        """
        return self.donations
    

    def update_donations(self,donation):
        self.donations = donation


def find_project_index(projects, project_name):
    """
    Finds the index of a project in the list of projects.

    Parameters
    ----------
        projects : list
            A list of Project objects.
        project_name : str
            The name of the project to find.

    Returns
    -------
        int
            The index of the project in the list, or -1 if not found.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> projects = [project_A, project_B, project_C]
    >>> find_project_index(projects, "B")
    1
    >>> find_project_index(projects, "D")
    -1
    """
    return next((i for i, project in enumerate(projects) if project.get_name() == project_name), -1)


def get_project_names(projects):
    """
    Gets the names of projects in a list of projects.

    Parameters
    ----------
        projects : list
            A list of Project objects.

    Returns
    -------
        list
            A list of project names.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> projects = [project_A, project_B, project_C]
    >>> get_project_names(projects)
    ['A', 'B', 'C']
    """
    return [project.name for project in projects]


def reset_donations(projects, index):
    """
    Resets the donations of a project.

    Parameters
    ----------
        projects : list
            A list of Project objects.
        index : int
            The index of the project to reset.

    Returns
    -------
        list
            The list of projects with donations reset.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> project_A.update_support([5, 10, 0, 0, 15])
    >>> project_B.update_support([10, 10, 15, 0, 5])
    >>> project_C.update_support([5, 0, 5, 20, 0])
    >>> projects = [project_A, project_B, project_C]
    >>> updated_projects = reset_donations(projects, 0)
    >>> for project in updated_projects:
    ...     print(f"{project.name}: {project.support}")
    A: [0, 0, 0, 0, 0]
    B: [10, 10, 15, 0, 5]
    C: [5, 0, 5, 20, 0]
    """
    for project in projects:
        if project == projects[index]:
            project.support = [0 for supporter in project.support]
    return projects



def calculate_total_initial_support(projects):
    """
    Calculates the total initial support for all projects.

    Parameters
    ----------
        projects : list
            A list of Project objects.

    Returns
    -------
        Numeric
            The total initial support for all projects.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> project_A.update_support([5, 10, 0, 0, 15])
    >>> project_B.update_support([10, 10, 15, 0, 5])
    >>> project_C.update_support([5, 0, 5, 20, 0])
    >>> projects = [project_A, project_B, project_C]
    >>> calculate_total_initial_support(projects)
    100
    """
    return sum(sum(project.support) for project in projects)

def calculate_total_initial_support_doners(doners):
    """
    Calculates the total initial support from all doners.

    Parameters
    ----------
        doners : list
            A list of doners objects.

    Returns
    -------
        Numeric
            The total initial support from all doners.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> doner1 = Doner([5, 10, 5])
    >>> doner2 = Doner([10, 10, 0])
    >>> doner3 = Doner([0, 15, 5])
    >>> doner4 = Doner([0, 0, 20])
    >>> doner5 = Doner([15, 5, 0])
    >>> doners = [doner1,doner2,doner3,doner4,doner5]
    >>> calculate_total_initial_support_doners(doners)
    100
    """
    return sum(sum(doner.get_donations()) for doner in doners)

def calculate_excess_support(project):
    """
    Calculates the excess support for a project.

    Parameters
    ----------
        project : Project
            The project for which to calculate excess support.

    Returns
    -------
        Numeric
            The excess support for the project.

    >>> project_A = Project("A", 27)
    >>> project_A.update_support([5, 10, 0, 0, 15])
    >>> calculate_excess_support(project_A)
    3
    """
    return sum(project.support) - project.cost



def select_max_excess_project(projects):
    """
    Selects the project with the maximum excess support.

    Parameters
    ----------
        projects : list
            A list of Project objects.

    Returns
    -------
        tuple
            A tuple containing the project with maximum excess support and the excess support value.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> project_A.update_support([5, 10, 0, 0, 15])
    >>> project_B.update_support([10, 10, 15, 0, 5])
    >>> project_C.update_support([5, 0, 5, 20, 0])
    >>> projects = [project_A, project_B, project_C]
    >>> max_excess_project, excess_support = select_max_excess_project(projects)
    >>> max_excess_project.name
    'B'
    >>> excess_support
    10
    """
    excess_support = {project: calculate_excess_support(project) for project in projects}
    max_excess_project = max(excess_support, key=excess_support.get)
    return max_excess_project, excess_support[max_excess_project]



def distribute_excess_support(projects, max_excess_project, doners, gama):
    """
    Distributes excess support from a project to other projects.

    Parameters
    ----------
        projects : list
            A list of Project objects.
        max_excess_project : Project
            The project with maximum excess support.
        doners : list
            A list of Doner objects.
        gama : Numeric
            The gamma value for distributing excess support.

    Returns
    -------
        list
            The list of projects after distributing excess support.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> doner1 = Doner([5, 10, 5])
    >>> doner2 = Doner([10, 10, 0])
    >>> doner3 = Doner([0, 15, 5])
    >>> doner4 = Doner([0, 0, 20])
    >>> doner5 = Doner([15, 5, 0])
    >>> project_A.update_support([5, 10, 0, 0, 15])
    >>> project_B.update_support([10, 10, 15, 0, 5])
    >>> project_C.update_support([5, 0, 5, 20, 0])
    >>> projects = [project_A, project_B, project_C]
    >>> doners = [doner1, doner2, doner3, doner4, doner5]
    >>> max_excess_project = project_A
    >>> gama = 0.5
    >>> updated_projects = distribute_excess_support(projects, max_excess_project, doners, gama)
    >>> for project in updated_projects:
    ...     print(f"{project.name}: {project.support}")
    A: [5, 10, 0, 0, 15]
    B: [15.0, 15.0, 15, 0, 7.5]
    C: [7.5, 0.0, 5, 20, 0.0]
    """
    max_index = find_project_index(projects, max_excess_project.get_name())
    for project in projects:
        if project.get_name() != max_excess_project.get_name():
            for j, supporter in enumerate(project.support):
                if doners[j].get_donations()[max_index] != 0:
                    project.support[j] += supporter * (1 - gama)
    return projects



def update_projects_support(projects, doners):
    """
    Performs cumulative budgeting using participatory budgeting with cumulative votes.

    Parameters
    ----------
    projects : list
        A list of Project objects.
    doners : list
        A list of Doner objects.

    Returns
    -------
    list
        A list of selected projects based on the budget.

    Examples
    --------
    >>> project1 = Project("Project 1", 100)
    >>> project2 = Project("Project 2", 200)
    >>> projects = [project1, project2]

    >>> doner1 = Doner([50, 150])
    >>> doner2 = Doner([100, 50])
    >>> doners = [doner1, doner2]

    >>> selected_projects = update_projects_support(projects, doners)
    >>> all(isinstance(project, Project) for project in selected_projects)
    True
    """
    for i, project in enumerate(projects):
        don = []
        for doner in doners:
            don.append(doner.get_donations()[i])
        project.update_support(don)
    
    return projects





def cstv_budgeting(projects, doners):
    """
    Performs cumulative budgeting using participatory budgeting with cumulative votes.

    Parameters
    ----------
        projects : list
            A list of Project objects.
        doners : list
            A list of Doner objects.
        budget : Numeric
            The budget available for funding projects.

    Returns
    -------
        list
            A list of selected projects based on the budget.

    >>> project_A = Project("A", 37)
    >>> project_B = Project("B", 30)
    >>> project_C = Project("C", 40)
    >>> doner1 = Doner([5, 10, 5])
    >>> doner2 = Doner([10, 10, 0])
    >>> doner3 = Doner([0, 15, 5])
    >>> doner4 = Doner([0, 0, 20])
    >>> doner5 = Doner([15, 5, 0])
    >>> project_A.update_support([5, 10, 0, 0, 15])
    >>> project_B.update_support([10, 10, 15, 0, 5])
    >>> project_C.update_support([5, 0, 5, 20, 0])
    >>> projects = [project_A, project_B, project_C]
    >>> doners = [doner1, doner2, doner3, doner4, doner5]
    >>> selected_projects = cstv_budgeting(projects, doners)
    >>> for project in selected_projects:
    ...     print(f"Selected Project: {project.name}, Cost: {project.cost}")
    Selected Project: B, Cost: 30
    Selected Project: A, Cost: 37
    """
    # Check if all elements in the projects list are instances of the Project class
    if not all(isinstance(project, Project) for project in projects):
        raise TypeError("All elements in the 'projects' list must be instances of the 'Project' class.")

    # Check if all elements in the doners list are instances of the Doner class
    if not all(isinstance(doner, Doner) for doner in doners):
        raise TypeError("All elements in the 'doners' list must be instances of the 'Doner' class.")
    selected_projects = []
    budget = calculate_total_initial_support(projects)
    while True:
        max_excess_project, excess = select_max_excess_project(projects)
        if excess <= 0:
            break
        selected_projects.append(max_excess_project)
        gama = max_excess_project.get_cost() / (excess + max_excess_project.get_cost())
        projects = distribute_excess_support(projects, max_excess_project, doners, gama)
        k = find_project_index(projects, max_excess_project.get_name())
        projects = reset_donations(projects, k)
        budget -= max_excess_project.cost
        projects = [project for project in projects if project.cost <= budget]
        if not projects:
            break
    return selected_projects



if __name__ == "__main__":
    import doctest
    doctest.testmod()
    