
Satisfaction Measures
=====================

In participatory budgeting, various concepts and rules utilize proxies for voter satisfaction,
which are deduced from the submitted ballots rather than using the ballots directly.

We offer a range of satisfaction functions and provide flexible ways to create custom ones.
A satisfaction function is represented by a class that inherits from
:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`.
Such a class is initialized with specific parameters: an instance, a profile, and a ballot.
The class implements a `sat` method used to compute the satisfaction value for that
particular ballot. Additionally, we introduce
:py:class:`~pabutools.election.satisfaction.satisfactionprofile.SatisfactionProfile`,
a class that inherits from the Python class `list` and facilitates managing a collection
of satisfaction functions. We also have
:py:class:`~pabutools.election.satisfaction.satisfactionprofile.SatisfactionMultiProfile`,
which represents satisfaction profiles as multisets (see our discussion above about multiprofiles).

The typical workflow involves gathering the ballots into a profile, converting them
into a collection of satisfaction functions, and then using these functions as input to a rule.


.. code-block:: python

    from pabutools.election import SatisfactionProfile, SatisfactionMeasure
    from pabutools.election import parse_pabulib

    instance, profile = parse_pabulib("path_to_the_file")
    sat_profile = SatisfactionProfile(instance=instance)

    # We define a satisfaction function:
    class MySatisfaction(SatisfactionMeasure):
        def sat(self, projects):
            return 100 if "p1" in projects else len(projects)

    # We populate the satisfaction profile
    for ballot in profile:
        sat_profile.append(MySatisfaction(instance, profile, ballot))

    # The satisfaction profile is ready for use
    outcome = rule(sat_profile)


To simplify the process of defining the satisfaction profile, we offer convenient
methods and provide several widely used satisfaction functions.

.. code-block:: python

    from pabutools.election import SatisfactionProfile, Cardinality_Sat
    from pabutools.election import parse_pabulib

    instance, profile = parse_pabulib("path_to_the_file")
    # If a profile and a sat_class are given to the constructor, the satisfaction profile
    # is directly initialized with one instance of the sat_class per ballot in the profile.
    sat_profile = SatisfactionProfile(instance=instance, profile=profile, sat_class=Cardinality_Sat)
    # The satisfaction profile is ready for use
    outcome = rule(sat_profile)

Default Satisfaction Functions
------------------------------

Several satisfaction functions are already defined in the package and can be imported
from `pabutools.election`. We list them below.

- :py:class:`~pabutools.election.satisfaction.functionalsatisfaction.CC_Sat` implements the Chamberlin-Courant satisfaction function.
- :py:class:`~pabutools.election.satisfaction.functionalsatisfaction.Cost_Sqrt_Sat` defines the satisfaction as the square root of the total cost of the selected and approved projects.
- :py:class:`~pabutools.election.satisfaction.functionalsatisfaction.Cost_Log_Sat` defines the satisfaction as the log of the total cost of the approved and selected projects.
- :py:class:`~pabutools.election.satisfaction.additivesatisfaction.Cardinality_Sat` defines the satisfaction as the number of approved and selected projects.
- :py:class:`~pabutools.election.satisfaction.additivesatisfaction.Relative_Cardinality_Sat` defines the satisfaction as the number of approved and selected projects divided by the size the largest feasible subset of the ballot.
- :py:class:`~pabutools.election.satisfaction.additivesatisfaction.Cost_Sat` defines the satisfaction as the total cost of the approved and selected projects.
- :py:class:`~pabutools.election.satisfaction.additivesatisfaction.Relative_Cost_Sat` defines the satisfaction as the total cost of the approved and selected projects divided by the total cost of the most expensive subset of the ballot.
- :py:class:`~pabutools.election.satisfaction.additivesatisfaction.Relative_Cost_Approx_Normaliser_Sat` resembles the previous but uses the total cost of the ballot as the normalizer.
- :py:class:`~pabutools.election.satisfaction.additivesatisfaction.Effort_Sat` defines the satisfaction as the total share of a voter, i.e., the sum over all approved and selected projects of the cost divided by the approval score.
- :py:class:`~pabutools.election.satisfaction.additivesatisfaction.Additive_Cardinal_Sat` defines the satisfaction as the sum of the scores of the selected projects, where the scores are taken from the cardinal ballot of the voter.
- :py:class:`~pabutools.election.satisfaction.positionalsatisfaction.Additive_Borda_Sat` defines the satisfaction as the sum of the Borda scores of the selected projects.

Next, we present additional tools we provide to define satisfaction functions.

Functional Satisfaction Functions
---------------------------------

For more specific ways of defining satisfaction functions, we introduce the class
:py:class:`~pabutools.election.satisfaction.functionalsatisfaction.FunctionalSatisfaction`.
This class corresponds to a satisfaction function defined by a function that takes as arguments
an instance, a profile, a ballot, and a set of projects. To demonstrate its use, we illustrate
how to define the Chamberlin-Courant satisfaction function with approval (equal to 1 if
at least one approved project is selected and 0 otherwise).

.. code-block:: python

    from pabutools.election import FunctionalSatisfaction

    def cc_sat_func(instance, profile, ballot, projects):
        return int(any(p in ballot for p in projects))

    class CC_Sat(FunctionalSatisfaction):
            def __init__(self, instance, profile, ballot):
                super(CC_Sat, self).__init__(instance, profile, ballot, cc_sat_func)



Additive Satisfaction Functions
-------------------------------

We also offer additive satisfaction functions, where the satisfaction for a set
of projects is equal to the sum of the satisfaction of each individual project. The class
:py:class:`~pabutools.election.satisfaction.additivesatisfaction.AdditiveSatisfaction`
implements such functions. Its constructor takes a function as a parameter that maps
instance, profile, ballot, project, and pre-computed values to a score. The pre-computed
argument is used to pass fixed parameters to the function that can be used
for expensive computations not to be done more than once. As an example, we demonstrate
how to define the cardinality satisfaction function.

.. code-block:: python

    from pabutools.election import AdditiveSatisfaction

    def cardinality_sat_func(instance, profile, ballot, project, precomputed_values):
        return int(project in ballot)

    class Cardinality_Sat(AdditiveSatisfaction):
        def __init__(self, instance, profile, ballot):
            super(Cardinality_Sat, self).__init__(instance, profile, ballot, cardinality_sat_func)

Positional Satisfaction Functions
---------------------------------

For ordinal ballots, we have positional satisfaction functions, where a voter's
satisfaction depends on the position of projects in their ballot. The class
:py:class:`~pabutools.election.satisfaction.positionalsatisfaction.PositionalSatisfaction`
implements these functions. Its constructor takes two functions as parameters: one that maps
ballots and projects to a score and another that aggregates the individual scores for sets
of projects. As an example, we define the additive Borda satisfaction function.

.. code-block:: python

    from pabutools.election import PositionalSatisfaction

    def borda_sat_func(ballot, project):
        if project not in ballot:
            return 0
        return len(ballot) - ballot.index(project)

    class Additive_Borda_Sat(PositionalSatisfaction):
        def __init__(self, instance, profile, ballot):
            super(Additive_Borda_Sat, self).__init__(instance, profile, ballot, borda_sat_func, sum)
