Tie-Breaking
============

For reference, see the module :py:mod:`~pabutools.tiebreaking`.

We provide several ways to break ties between several projects. All tie-breaking rules are
instantiations of the :py:class:`~pabutools.tiebreaking.TieBreakingRule` class.
This class defines two functions `untie` and `order` that respectively return a single project
from a set of several or order a list of projects.

We profile several tie-breaking rules.

.. code-block:: python

    from pabutools.election import Project, Instance, ApprovalProfile, ApprovalBallot
    from pabutools.tiebreaking import max_cost_tie_breaking, min_cost_tie_breaking
    from pabutools.tiebreaking import app_score_tie_breaking, lexico_tie_breaking

    p = [Project("p0", 1), Project("p1", 2), Project("p2", 1)]
    instance = Instance(p, budget_limit=2)
    profile = ApprovalProfile([
        ApprovalBallot(p),
        ApprovalBallot(p[1:]),
        ApprovalBallot({p[1]})
    ])

    min_cost_tie_breaking.untie(instance, profile, [p[0], p[1]])   # Returns p0
    max_cost_tie_breaking.untie(instance, profile, [p[0], p[1]])   # Returns p1

    app_score_tie_breaking.untie(instance, profile, p)   # Returns p1
    app_score_tie_breaking.order(instance, profile, p)   # Returns [p1, p2, p0]

    lexico_tie_breaking.order(instance, profile, p)   # Returns [p0, p1, p2]

These are mainly used as arguments for the rules, as seen above.
