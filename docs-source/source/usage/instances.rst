Instances
=========

Please refer to the module :py:mod:`~pabutools.election.instance` for more information.

A participatory budgeting instance encapsulates all the elements defining the elections. It includes
the projects up for voting, along with the budget limit.

The central class is :py:class:`~pabutools.election.instance.Instance`.
This class inherits from the Python `set` class, behaving as a set of projects,
augmented with additional information. Projects are instances of the class
:py:class:`~pabutools.election.instance.Project`, which stores a project's name, cost,
and any potential additional information. Here's an example:

.. code-block:: python

    from pabutools.election import Instance, Project

    instance = Instance()   # It accepts several optional parameters
    p1 = Project("p1", 1)   # The constructor requires the name and cost of the project
    instance.add(p1)   ## Set methods are used to add/remove projects from an instance
    p2 = Project("p2", 1)
    instance.add(p2)
    p3 = Project("p3", 3)
    instance.add(p3)

Notably, any Python comparison between two projects (equality, etc.) is based on the
name of the projects. Since an instance is a set, adding a project `Project("p", 1)` and
another project `Project("p", 3)` will result in an instance with a single project.

An instance also stores additional information such as the budget limit of the election
and additional metadata.

.. code-block:: python

    instance.budget_limit = 3   # The budget limit
    instance.meta   # dict storing metadata on the instance
    instance.project_meta   # dict of (project, dict) storing metadata on the projects

An instance can invoke several methods to iterate through all the budget allocations,
test the feasibility of a set of projects, and so on.

.. code-block:: python

    for b in instance.budget_allocations():
        print(str(b) + " is a feasible budget allocation")
    instance.is_feasible([p1, p2, p3])   # Returns False
    instance.is_exhaustive([p1, p2])   # Returns True