from collections.abc import Iterable

from pabutools.election.instance import Project

from collections.abc import Collection
from pabutools.utils import Numeric


class AllocationDetails:
    """
    Class representing participatory budgeting rule run details.
    Used as a parent class which can be inherited.
    """

    def __init__(self):
        pass


class MESAllocationDetails(AllocationDetails):
    """
    Class representing the details of MES rule.
    This class represents the MES details using an iteration approach: at each iteration of the MES rule some
    crucial informations are saved which allow for reconstruction of the whole run. Iteration happens whenever
    a project got picked or discraded during a run.

    Parameters
    ----------
        initial_budget_per_voter: Numeric
            Describes the starting budget of each voter.


    Attributes
    ----------
        initial_budget_per_voter: Numeric
            Describes the starting budget of each voter.
        iterations: Iterable[:py:class:`~pabutools.rules.budgetallocation.MESIteration`]
            A list of all iterations of a MES rule run. It is progressively populated during a MES rule run.
    """
    def __init__(
        self,
        initial_budget_per_voter: Numeric,
    ):
        self.initial_budget_per_voter: Numeric = initial_budget_per_voter
        self.iterations: list[MESIteration] = []

    def __str__(self):
        return f"MESAllocationDetails[{self.iterations}]"

    def __repr__(self):
        return f"MESAllocationDetails[{self.iterations}]"


class MESIteration:
    """
    Class representing a single iteration of a MES rule run, solely used in :py:class:`~pabutools.rules.budgetallocation.MESAllocationDetails`
    Each iteration consist of information necessary for reconstructing a MES rule run. This includes the project the iteration is about, its
    supporters, whether it was picked or discarded, and the voters budgets after potential 'purchase' of the project.

    Parameters
    ----------
        project: :py:class:`~pabutools.election.instance.Project`
            The project that was considered by a MES iteration.
        supporter_indices: list[int]
            Stores all indices of voters which supported the aforementioned project. 
            Those indices match with indices of voters_budget attribute.
        was_picked: bool
            Indicates whether the aforementioned project was picked or discraded by MES.
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
            Indicates whether the aforementioned project was picked or discraded by MES.
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


class BudgetAllocation(list[Project]):
    """
    A budget allocation is the outcome of rule. It simply corresponds to a list of projects.
    Additional information can also be stored in this class, for instance for explanation purposes.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.instance.Project`], optional
            An iterable of :py:class:`~pabutools.election.instance.Project` that is used an
            initializer for the list.
        details: :py:class:`~pabutools.rules.budgetallocation.AllocationDetails`, optional
            Used for storing various additional information about a participatory budgeting rule run.
            Defaults to None.

    Attributes
    ----------
        details: :py:class:`~pabutools.rules.budgetallocation.AllocationDetails`, optional
            Used for storing various additional information about a participatory budgeting rule run.
            Defaults to None.

    """

    def __init__(
        self,
        init: Iterable[Project] = (),
        details: AllocationDetails | None = None
    ) -> None:
        list.__init__(self, init)
        if details is None:
            if isinstance(init, BudgetAllocation):
                details = init.details
        self.details = details

    # Ensures that methods returning copies of sets cast back into BudgetAllocation
    @classmethod
    def _wrap_methods(cls, methods):
        def wrap_method_closure(method):
            def inner_method(self, *args):
                result = getattr(super(cls, self), method)(*args)
                if isinstance(result, list) and not isinstance(result, cls):
                    result = cls(init=result, details=self.details)
                return result

            inner_method.fn_name = method
            setattr(cls, method, inner_method)

        for m in methods:
            wrap_method_closure(m)


BudgetAllocation._wrap_methods(
    [
        "__add__",
        "__iadd__",
        "__imul__",
        "__mul__",
        "__reversed__",
        "__rmul__",
        "copy",
        "reverse",
        "__getitem__",
    ]
)
