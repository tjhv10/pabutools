from __future__ import annotations

from typing import Tuple

from pabutools.utils import Numeric
from pabutools.election import Project
from pabutools.rules.budgetallocation import AllocationDetails


class ProjectLoss(Project):
    """
    Class used to represent the projects and how much budget they lost due to other projects being picked.

    Parameters
    ----------
        project: Project
            Project for which analytics is calculated.
        supporters_budget: Numeric
            The collective budget of the project supporters when project was considered by a rule.
        budget_lost: dict[Project, Numeric]
            Describes the amount of budget project supporters spent on other projects prior to this
            projects' consideration.

    Attributes
    ----------
        project: Project
            Project for which analytics is calculated.
        supporters_budget: Numeric
            The collective budget of the project supporters when project was considered by rule.
        budget_lost: dict[Project, Numeric]
            Describes the amount of budget project supporters spent on other projects prior to this
            projects' consideration.
    """

    def __init__(
        self,
        project: Project,
        supporters_budget: Numeric,
        budget_lost: dict[Project, Numeric],
    ):
        Project.__init__(
            self, project.name, project.cost, project.categories, project.targets
        )
        self.supporters_budget: Numeric = supporters_budget
        self.budget_lost: dict[Project, Numeric] = budget_lost

    def total_budget_lost(self) -> Numeric:
        """
        Returns the total budget spent by project supporters on prior projects.

        Returns
        -------
            Numeric
                The total budget spent.
        """
        return sum(self.budget_lost.values())

    def __str__(self):
        return f"ProjectLoss[{self.name}, {float(self.supporters_budget)}, {self.total_budget_lost()}]"

    def __repr__(self):
        return f"ProjectLoss[{self.name}, {float(self.supporters_budget)}, {self.total_budget_lost()}]"


def calculate_project_loss(
    allocation_details: AllocationDetails, verbose: bool = False
) -> list[ProjectLoss]:
    if (
        allocation_details.iterations is None
        or allocation_details.initial_budget_per_voter is None
    ):
        raise ValueError(
            "Provided allocation details do not support calculating project loss"
        )
    if len(allocation_details.iterations) == 0:
        if verbose:
            print(f"Rule did not have any iterations, returning empty list")
        return []

    project_losses = []
    voter_count = len(allocation_details.iterations[0].voters_budget)
    voter_spendings: dict[int, list[Tuple[Project, Numeric]]] = {}
    for idx in range(voter_count):
        voter_spendings[idx] = []

    current_voters_budget = [
        allocation_details.initial_budget_per_voter for _ in range(voter_count)
    ]

    for iter in allocation_details.iterations:
        if verbose:
            print(f"Considering: {iter.project.name}, status: {iter.was_picked}")
        budget_lost = {}
        for spending in [voter_spendings[i] for i in iter.supporter_indices]:
            for project, spent in spending:
                if project not in budget_lost.keys():
                    budget_lost[project] = 0
                budget_lost[project] = budget_lost[project] + spent
        project_losses.append(
            ProjectLoss(
                iter.project,
                sum(current_voters_budget[i] for i in iter.supporter_indices),
                budget_lost,
            )
        )
        if iter.was_picked:
            for supporter_idx in iter.supporter_indices:
                voter_spendings[supporter_idx].append(
                    (
                        iter.project,
                        current_voters_budget[supporter_idx]
                        - iter.voters_budget[supporter_idx],
                    )
                )
            current_voters_budget = iter.voters_budget           

    return project_losses
