.. _outcome-visualisation:

Outcome Visualisation
=====================

For reference, see the module :py:mod:`~pabutools.visualisation`.

We provide the visualisation for the outcomes of :py:func:`~pabutools.rules.greedywelfare.greedy_utilitarian_welfare` and :py:func:`~pabutools.rules.mes.method_of_equal_shares`. This explains in depth the outcome of the election based on the chosen rule. This includes which projects were selected or rejected, summary statistics about the election, and rule specific information such as effective vote count in :py:func:`~pabutools.rules.mes.method_of_equal_shares`. The chart libraries we use are ZingChart and Google Developer Charts, and the visualisations are saved as HTML files.

Note that selecting the visualisation option will increase the runtime of the election, however without this option, the runtime will remain the same.

Greedy Utilitarian Welfare
--------------------------

The visualisation for the Greedy Utilitarian Welfare currently works only on additive utility functions.

We provide a way to visualise the results using the class
:py:class:`~pabutools.visualisation.GreedyWelfareVisualiser`. Note the analytics flag in the
function :py:func:`~pabutools.rules.greedywelfare.greedy_utilitarian_welfare` must be set to True to
generate the visualisation.

.. code-block:: python

    from pabutools.visualisation.visualisation import GreedyWelfareVisualiser
    from pabutools.rules.greedywelfare import greedy_utilitarian_welfare
    from pabutools import election
    from pabutools.election import Cost_Sat

    instance, profile = election.parse_pabulib("./{path_to_election_file}.pb")
    outcome = greedy_utilitarian_welfare(instance, profile, sat_class=Cost_Sat, analytics=True)

    # The visualiser takes the profile, instance, and outcome as arguments
    visualiser = GreedyWelfareVisualiser(profile, instance, outcome)

    # name is optional and defaults to the empty string
    visualiser.render("./{path_to_output_file}/", name="{name}")

The visualisation will be saved in the specified path as a standalone HTML file called "{name}_round_analysis.html". 

Note that the visualisation is only available for additive utility functions.

An example of the generated visualisation can be found
`here <../outcome_vis_ex_greedy.html>`__.

Method of Equal Shares
----------------------

We provide a way to visualise the results using the class :py:class:`~pabutools.visualisation.MESVisualiser`.
Note the analytics flag in the function
:py:func:`~pabutools.rules.mes.method_of_equal_shares` must be set to True to generate the visualisation.
The visualisations for MES consist of two pages: one for the summary of the election, containing the
allocation of the budget, information about all the elected projects, and summary statistics about
the election as a whole. The second page contains the details of the election, giving statistics
about each round of the election, including the selected project, and how each round impacts
the effective vote count of others. This captures the essence of the method of equal shares, where
the effective vote count of each project is updated after each round.

.. code-block:: python

    from pabutools.visualisation.visualisation import MESVisualiser
    from pabutools.rules.mes import method_of_equal_shares
    from pabutools import election
    from pabutools.election import Cost_Sat

    instance, profile = election.parse_pabulib("./{path_to_election_file}.pb")
    outcome = method_of_equal_shares(instance, profile, sat_class=Cost_Sat, analytics=True)

    # The visualiser takes the profile, instance, and outcome as arguments
    visualiser = MESVisualiser(profile, instance, outcome)

    # name is optional and defaults to the empty string
    visualiser.render("./{path_to_output_file}/", name="{name}")

The visualisations will be saved with the filenames {name}_summary.html and
{name}_round_analysis.html respectively in the specified path. These work as standalone HTML files,
and must be stored in the same directory to ensure the links between different pages work correctly.

An example of the generated visualisation can be found
`here <../outcome_vis_ex_mes_summary.html>`__.