Fractions
=========

For reference, see the module :py:mod:`~pabutools.fractions`.

We provide a customizable way to handle fractions. In general, all fractions should be defined
using the :py:func:`~pabutools.fractions.frac` function provided in the :py:mod:`~pabutools.fractions`
module. Not doing so may lead to undesirable behaviors (i.e., errors).

To make a fraction, simply follow this guide:

.. code-block:: python

    from pabutools.fractions import frac, str_as_frac

    # Define a fraction
    fraction = frac(1, 4)

    # Define a fraction from an integer
    fraction_from_int = frac(2)

    # Define a fraction from a float
    fraction_from_int = frac(2.6)

    # Define a fraction from a string
    fraction_from_str = str_as_frac("2.3")

By default, the `gmpy2 <https://gmpy2.readthedocs.io/en/latest/mpq.html>`_ module is used to
handle fractions. To change this, simply change the value of the `FRACTION` constant.

.. code-block:: python

    import pabutools.fractions

    # The default value
    pabutools.fractions.FRACTION = "gmpy2"

    # Change to Python float
    pabutools.fractions.FRACTION = "float"

Changing the `FRACTION` constant changes the algorithm used to handle fractions.

