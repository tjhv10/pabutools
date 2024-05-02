from __future__ import annotations

import collections
from abc import ABC, abstractmethod

from mip import Model, xsum, minimize

from pabutools.election import (
    Instance,
    Profile,
    Project,
)


class Relaxation(ABC):
    def __init__(self, instance: Instance, profile: Profile):
        self.instance = self.C = instance
        self.profile = self.N = profile
        self.INF = instance.budget_limit * 10
        self._saved_beta = None

    @abstractmethod
    def add_beta(self, mip_model: Model) -> None:
        pass

    @abstractmethod
    def add_objective(self, mip_model: Model) -> None:
        pass

    @abstractmethod
    def add_stability_constraint(self, mip_model: Model) -> None:
        pass

    @abstractmethod
    def get_beta(self, mip_model: Model):
        pass

    @abstractmethod
    def get_relaxed_cost(self, project: Project) -> float:
        pass


class MinMul(Relaxation):
    def add_beta(self, mip_model: Model) -> None:
        mip_model.add_var(name="beta")

    def add_objective(self, mip_model: Model) -> None:
        beta = mip_model.var_by_name(name="beta")
        mip_model.objective = minimize(beta)

    def add_stability_constraint(self, mip_model: Model) -> None:
        x_vars = {c: mip_model.var_by_name(name=f"x_{c.name}") for c in self.C}
        m_vars = [mip_model.var_by_name(name=f"m_{idx}") for idx, _ in enumerate(self.N)]
        beta = mip_model.var_by_name(name="beta")
        for c in self.C:
            mip_model += xsum(m_vars[idx] for idx, i in enumerate(self.N) if c in i) <= c.cost * beta + x_vars[c] * self.INF

    def get_beta(self, mip_model: Model):
        beta = mip_model.var_by_name(name="beta")
        self._saved_beta = beta.x
        return self._saved_beta

    def get_relaxed_cost(self, project: Project) -> float:
        return project.cost * self._saved_beta

class MinAdd(Relaxation):
    def add_beta(self, mip_model: Model) -> None:
        mip_model.add_var(name="beta", lb=-self.INF)

    def add_objective(self, mip_model: Model) -> None:
        beta = mip_model.var_by_name(name="beta")
        mip_model.objective = minimize(beta)

    def add_stability_constraint(self, mip_model: Model) -> None:
        x_vars = {c: mip_model.var_by_name(name=f"x_{c.name}") for c in self.C}
        m_vars = [mip_model.var_by_name(name=f"m_{idx}") for idx, _ in enumerate(self.N)]
        beta = mip_model.var_by_name(name="beta")
        for c in self.C:
            mip_model += xsum(m_vars[idx] for idx, i in enumerate(self.N) if c in i) <= c.cost + beta + x_vars[c] * self.INF

    def get_beta(self, mip_model: Model):
        beta = mip_model.var_by_name(name="beta")
        self._saved_beta = beta.x
        return self._saved_beta

    def get_relaxed_cost(self, project: Project) -> float:
        return project.cost + self._saved_beta

class MinAddVector(Relaxation):
    def add_beta(self, mip_model: Model) -> None:
        beta = {c: mip_model.add_var(name=f"beta_{c.name}", lb=-self.INF) for c in self.C}
        x_vars = {c: mip_model.var_by_name(name=f"x_{c.name}") for c in self.C}
        # beta[c] is zero for selected
        for c in self.C:
            mip_model += beta[c] <= (1 - x_vars[c]) * self.instance.budget_limit
            mip_model += (x_vars[c] - 1) * self.instance.budget_limit <= beta[c]

    def add_objective(self, mip_model: Model) -> None:
        beta = {c: mip_model.var_by_name(name=f"beta_{c.name}") for c in self.C}
        mip_model.objective = minimize(xsum(beta[c] for c in self.C))

    def add_stability_constraint(self, mip_model: Model) -> None:
        x_vars = {c: mip_model.var_by_name(name=f"x_{c.name}") for c in self.C}
        m_vars = [mip_model.var_by_name(name=f"m_{idx}") for idx, _ in enumerate(self.N)]
        beta = {c: mip_model.var_by_name(name=f"beta_{c.name}") for c in self.C}
        for c in self.C:
            mip_model += xsum(m_vars[idx] for idx, i in enumerate(self.N) if c in i) <= c.cost + beta[c] + x_vars[c] * self.INF

    def get_beta(self, mip_model: Model):
        beta = {c: mip_model.var_by_name(name=f"beta_{c.name}") for c in self.C}
        return_beta = collections.defaultdict(int)
        for c in self.C:
            if beta[c].x:
                return_beta[c] = beta[c].x
        self._saved_beta = {"beta": return_beta, "sum": sum(return_beta.values())}
        return self._saved_beta

    def get_relaxed_cost(self, project: Project) -> float:
        return project.cost + self._saved_beta["beta"][project]


class MinAddVectorPositive(MinAddVector):
    def add_beta(self, mip_model: Model) -> None:
        _beta = {c: mip_model.add_var(name=f"beta_{c.name}") for c in self.C}


class MinAddOffset(Relaxation):
    BUDGET_FRACTION = 0.025

    def add_beta(self, mip_model: Model) -> None:
        _beta_global = mip_model.add_var(name="beta", lb=-self.INF)
        beta = {c: mip_model.add_var(name=f"beta_{c.name}") for c in self.C}
        mip_model += xsum(beta[c] for c in self.C) <= self.BUDGET_FRACTION * self.instance.budget_limit

    def add_objective(self, mip_model: Model) -> None:
        beta_global = mip_model.var_by_name(name="beta")
        mip_model.objective = minimize(beta_global)

    def add_stability_constraint(self, mip_model: Model) -> None:
        x_vars = {c: mip_model.var_by_name(name=f"x_{c.name}") for c in self.C}
        m_vars = [mip_model.var_by_name(name=f"m_{idx}") for idx, _ in enumerate(self.N)]
        beta_global = mip_model.var_by_name(name="beta")
        beta = {c: mip_model.var_by_name(name=f"beta_{c.name}") for c in self.C}
        for c in self.C:
            mip_model += xsum(m_vars[idx] for idx, i in enumerate(self.N) if c in i) <= c.cost + beta_global + beta[c] + x_vars[c] * self.INF

    def get_beta(self, mip_model: Model):
        beta_global = mip_model.var_by_name(name="beta")
        beta = {c: mip_model.var_by_name(name=f"beta_{c.name}") for c in self.C}
        return_beta = collections.defaultdict(int)
        for c in self.C:
            if beta[c].x:
                return_beta[c] = beta[c].x
        self._saved_beta = {"beta": return_beta, "beta_global": beta_global.x, "sum": sum(return_beta.values())}
        return self._saved_beta

    def get_relaxed_cost(self, project: Project) -> float:
        return project.cost + self._saved_beta["beta_global"] + self._saved_beta["beta"][project]
