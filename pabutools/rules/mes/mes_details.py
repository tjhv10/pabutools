from pabutools.election.instance import Project
from pabutools.rules.budgetallocation import AllocationDetails
from pabutools.utils import Numeric


class MESAllocationDetails(AllocationDetails):
    """Class representing the details of MES rule.
    This class represents the MES details using an iteration approach: at each iteration of the MES rule some
    crucial information is saved which allow for reconstruction of the whole run. Iteration happens whenever
    a project got picked or discarded during a run.

    Parameters
    ----------
        initial_budget_per_voter: :py:class:`~pabutools.utils.Numeric`
            Describes the starting budget of each voter.


    Attributes
    ----------
        initial_budget_per_voter: :py:class:`~pabutools.utils.Numeric`
            Describes the starting budget of each voter.
        iterations: Iterable[:py:class:`~pabutools.rules.mes.MESIteration`]
            A list of all iterations of a MES rule run. It is progressively populated during a MES rule run.
    """

    def __init__(self, initial_budget_per_voter: Numeric, voter_multiplicity: list[int]):
        super().__init__()
        self.initial_budget_per_voter: Numeric = initial_budget_per_voter
        self.voter_multiplicity: list[int] = voter_multiplicity
        self.iterations: list[MESIteration] = []

    def __str__(self):
        return f"MESAllocationDetails[{self.iterations}]"

    def __repr__(self):
        return f"MESAllocationDetails[{self.iterations}]"


class MESIteration:
    """Class representing a single iteration of a MES rule run, solely used in
    :py:class:`~pabutools.rules.mes.MESAllocationDetails`. Each iteration consist of information
    necessary for reconstructing a MES rule run. This includes the project the iteration is about, its supporters,
    whether it was picked or discarded, and the voters budgets after potential 'purchase' of the project.

    Parameters
    ----------
        project: :py:class:`~pabutools.election.instance.Project`
            The project that was considered by a MES iteration.
        supporter_indices: list[int]
            Stores all indices of voters which supported the aforementioned project.
            Those indices match with indices of voters_budget attribute.
        was_picked: bool
            Indicates whether the aforementioned project was picked or discarded by MES.
        voters_budget: list[int], optional
            Describes the budget of each voter at the current iteration. If a project was picked, then the voters budgets
            describe the state after the purchase. If the project wasn't picked, it stays the same (compared to previous iteration).
            Defaults to `[]`.


    Attributes
    ----------
        project: :py:class:`~pabutools.election.instance.Project`
            The project that was considered by a MES iteration.
        supporter_indices: list[int]
            Stores all indices of voters which supported the aforementioned project.
            Those indices match with indices of voters_budget attribute.
        was_picked: bool
            Indicates whether the aforementioned project was picked or discarded by MES.
        voters_budget: list[int], optional
            Describes the budget of each voter at the current iteration. If a project was picked, then the voters budgets
            describe the state after the purchase. If the project wasn't picked, it stays the same (compared to previous iteration).
            Defaults to `[]`.
    """

    def __init__(
        self,
        project: Project,
        supporter_indices: list[int],
        was_picked: bool,
        voters_budget: list[int] = [],
    ):
        self.project: Project = project
        self.supporter_indices: list[int] = supporter_indices
        self.was_picked: bool = was_picked
        self.voters_budget: list[int] = voters_budget

    def __str__(self):
        return f"MESIteration[Project: {self.project.name} {'was picked' if self.was_picked else 'was not picked'}]"

    def __repr__(self):
        return f"MESIteration[Project: {self.project.name} {'was picked' if self.was_picked else 'was not picked'}]"
