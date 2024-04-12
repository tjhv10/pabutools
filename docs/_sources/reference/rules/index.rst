Rules module
============

.. automodule:: pabutools.rules

Budget Allocation
-----------------

.. autoclass:: pabutools.rules.budgetallocation.BudgetAllocation

.. autoclass:: pabutools.rules.budgetallocation.AllocationDetails

Greedy Utilitarian Rule
-----------------------

.. autofunction:: pabutools.rules.greedywelfare.greedy_utilitarian_welfare

.. autoclass:: pabutools.rules.greedywelfare.GreedyWelfareAllocationDetails

Additive Utilitarian Welfare Maximiser
--------------------------------------

.. autoenum:: pabutools.rules.maxwelfare.MaxAddUtilWelfareAlgo

.. autofunction:: pabutools.rules.maxwelfare.max_additive_utilitarian_welfare

Sequential Phragmén's Rule
--------------------------

.. autofunction:: pabutools.rules.phragmen.sequential_phragmen

Method of Equal Shares (MES)
----------------------------

.. autofunction:: pabutools.rules.mes.method_of_equal_shares

.. autoclass:: pabutools.rules.mes.MESAllocationDetails

.. autoclass:: pabutools.rules.mes.MESIteration

Exhaustion Methods
------------------

.. autofunction:: pabutools.rules.exhaustion.completion_by_rule_combination

.. autofunction:: pabutools.rules.exhaustion.exhaustion_by_budget_increase

Rule Composition
----------------

.. autofunction:: pabutools.rules.composition.popularity_comparison

.. autofunction:: pabutools.rules.composition.social_welfare_comparison
