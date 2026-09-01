"""
Attacks API Endpoints for ATLAS Attack Lab.
Allows running simulated conversational memory poisoning attacks and resetting testbeds.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from attacks.scenarios import ATTACK_SCENARIOS, AttackScenario
from attacks.poisoning_simulator import (
    poisoning_simulator,
    AttackSimulationResult
)

router = APIRouter(prefix="/attacks", tags=["Attack Lab"])


class RunAttackRequest(BaseModel):
    scenario_id: str
    enable_atlas: bool = True


@router.get("/scenarios", response_model=List[AttackScenario])
async def list_scenarios() -> List[AttackScenario]:
    """
    List all available attack scenarios (active prototypes and placeholders).
    """
    return ATTACK_SCENARIOS


@router.post("/run", response_model=AttackSimulationResult)
async def run_attack_scenario(request: RunAttackRequest) -> AttackSimulationResult:
    """
    Execute a conversational memory poisoning attack scenario against the agent.
    """
    try:
        return poisoning_simulator.run_simulation(
            scenario_id=request.scenario_id,
            enable_atlas=request.enable_atlas
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attack simulation error: {str(e)}")


@router.post("/reset")
async def reset_attack_lab() -> Dict[str, Any]:
    """
    Reset memory storage and restore academic baseline test state.
    """
    return poisoning_simulator.reset_environment()
