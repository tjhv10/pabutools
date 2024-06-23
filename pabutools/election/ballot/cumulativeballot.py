"""
Cumulative ballots, i.e., ballots in which the voters distribute a given amount of points to the projects.
"""

from __future__ import annotations

from abc import ABC

from pabutools.election.ballot.ballot import FrozenBallot, AbstractBallot
from pabutools.election.ballot.cardinalballot import (
    CardinalBallot,
    AbstractCardinalBallot,
)
from pabutools.election.instance import Project

from pabutools.utils import Numeric


class AbstractCumulativeBallot(AbstractCardinalBallot, ABC):
    """
    Abstract class for cumulative ballots. Essentially used for typing purposes.
    """

class FrozenCumulativeBallot(
    dict[Project, Numeric], FrozenBallot, AbstractCumulativeBallot
):
    def __init__(
        self,
        init: dict[Project, Numeric] | None = None,
        name: str | None = None,
        meta: dict | None = None,
    ):
        if init is None:
            init = dict()
        dict.__init__(self, init)
        if name is None:
            if isinstance(init, AbstractBallot):
                name = init.name
            else:
                name = ""
        if meta is None:
            if isinstance(init, AbstractBallot):
                meta = init.meta
            else:
                meta = dict()
        FrozenBallot.__init__(self, name=name, meta=meta)
        AbstractCumulativeBallot.__init__(self)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCumulativeBallot")

    def __hash__(self):
        return hash(frozenset(self.items()))

    def __eq__(self, other):
        if isinstance(other, FrozenCumulativeBallot):
            return dict(self) == dict(other)
        return False


class CumulativeBallot(CardinalBallot, AbstractCumulativeBallot):
    def __init__(
        self,
        init: dict[Project, Numeric] | None = None,
        name: str | None = None,
        meta: dict | None = None,
    ):
        if init is None:
            init = dict()
        if name is None:
            if isinstance(init, AbstractBallot):
                name = init.name
            else:
                name = ""
        if meta is None:
            if isinstance(init, AbstractBallot):
                meta = init.meta
            else:
                meta = dict()
        CardinalBallot.__init__(self, init, name=name, meta=meta)
        AbstractCumulativeBallot.__init__(self)

    def frozen(self) -> FrozenCumulativeBallot:
        return FrozenCumulativeBallot(self)

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(result, name=self.name, meta=self.meta)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)
    def __hash__(self):
        # Define hash based on immutable attributes of CumulativeBallot
        return hash(tuple(sorted(self.items())))
    def __eq__(self, other):
        if not isinstance(other, CumulativeBallot):
            return False
        return self.items() == other.items()

CumulativeBallot._wrap_methods(["copy", "__ior__", "__or__", "__ror__", "__reversed__"])
