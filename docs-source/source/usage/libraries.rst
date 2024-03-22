Preference Libraries
====================

See :ref:`preflibraries` for a reference.

We provide support for standard preference libraries.

PaBuLib
-------

Full support is provided for the participatory budgeting data hosted on the
`pabulib <http://pabulib.org>`_ website. You can use the function
:py:func:`~pabutools.election.pabulib.parse_pabulib` to parse a file
that conforms to the pabulib format. This function yields the instance
and profile based on the appropriate profile class determined by the ballot
format in the data.

.. code-block:: python

    from pabutools.election import parse_pabulib

    instance, profile = parse_pabulib("path_to_the_file")

Pabulib files contain an extensive range of metadata. This metadata is
stored in the `meta` members of the instance and profile classes.

.. code-block:: python

    from pabutools.election import parse_pabulib

    instance, profile = parse_pabulib("path_to_the_file")
    instance.meta   # The meta dict is populated with all the metadata described in the file
    instance.project_meta    # The project_meta dict is populated with the metadata related to the projects
    for ballot in profile:
        ballot.meta    # The meta dict populated with the metadata corresponding to the ballot

Several metadata is housed as members of the corresponding
classes. For example, all known constraints
that the voters were subjected to when submitting their ballots. This includes the minimum
length of a ballot or the number of points that must be allocated for instance.

.. code-block:: python

    ### For ApprovalProfile, CardinalProfile, CumulativeProfile, and OrdinalProfile
    profile.legal_min_length   # Imposed minimum length of the ballots in the profile
    profile.legal_max_length   # Imposed maximum length of the ballots in the profile

    ### For ApprovalProfile only
    profile.legal_min_cost   # Imposed minimum total cost of the ballots in the profile
    profile.legal_max_cost   # Imposed maximum total cost of the ballots in the profile

    ### For CardinalProfile and CumulativeProfile
    profile.legal_min_score   # Imposed minimum score assigned to a project for the ballots in the profile
    profile.legal_max_score   # Imposed maximum score assigned to a project for the ballots in the profile

    ### For CumulativeProfile only
    profile.legal_min_total_score   # Imposed minimum total scores for the ballots in the profile
    profile.legal_max_total_score   # Imposed maximum total scores for the ballots in the profile


It is also possible to write instances and profiles into Pabulib files:

.. code-block:: python

    from pabutools.election import write_pabulib

    write_pabulib(instance, profile, "path/to/the/file.pb")

If you need the string corresponding to the file content, you can use the following:

.. code-block:: python

    from pabutools.election.pabulib import election_as_pabulib_string

    str_representation = election_as_pabulib_string(instance, profile)


PrefLib
-------

In addition to `pabulib <http://pabulib.org>`_ , our package also supports the
`preflib <https://preflib.org>`_  format, providing functions to convert a participatory
budgeting election into a PrefLib instance.

.. code-block:: python

    from pabutools.election import Instance, ApprovalProfile, CardinalProfile, OrdinalProfile
    from pabutools.election import approval_to_preflib, cardinal_to_preflib, ordinal_to_preflib

    instance = Instance()

    # Approval profiles are mapped to categorical instances for PrefLib
    app_profile = ApprovalProfile()
    preflib_instance = approval_to_preflib(instance, app_profile)

    # Cardinal profiles are mapped to ordinal instances for PrefLib
    card_profile = CardinalProfile()
    preflib_instance = cardinal_to_preflib(instance, card_profile)

    # Ordinal profiles are mapped to ordinal instances for PrefLib
    ord_profile = ApprovalProfile()
    preflib_instance = ordinal_to_preflib(instance, ord_profile)
