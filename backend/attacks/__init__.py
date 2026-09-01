"""
Attacks package for ATLAS.
"""

from attacks.scenarios import (
    AttackScenario,
    ATTACK_SCENARIOS,
    get_scenario_by_id
)
from attacks.poisoning_simulator import (
    AttackSimulationResult,
    PoisoningSimulator,
    poisoning_simulator
)

__all__ = [
    "AttackScenario",
    "ATTACK_SCENARIOS",
    "get_scenario_by_id",
    "AttackSimulationResult",
    "PoisoningSimulator",
    "poisoning_simulator"
]
