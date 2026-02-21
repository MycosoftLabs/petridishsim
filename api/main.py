"""FastAPI service for Petri Dish chemical simulation."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from chemical.diffusion import ChemicalField, MultiCompoundField
from chemical.metabolism import MetabolicPathway
from chemical.reactions import ReactionDiffusionSystem

app = FastAPI(title="Petri Dish Sim", version="0.1.0")


class ChemicalStepRequest(BaseModel):
    fields: Dict[str, List[List[float]]]
    diffusion_rates: Dict[str, float]
    dt: float = Field(gt=0)
    decay_rates: Optional[Dict[str, float]] = None
    reaction_params: Dict[str, Dict[str, float]]


class ChemicalStepResponse(BaseModel):
    fields: Dict[str, List[List[float]]]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "healthy"}


@app.post("/chemical/step", response_model=ChemicalStepResponse)
async def chemical_step(payload: ChemicalStepRequest) -> ChemicalStepResponse:
    if not payload.fields:
        raise HTTPException(status_code=400, detail="fields must not be empty")

    first_field = next(iter(payload.fields.values()))
    height = len(first_field)
    width = len(first_field[0]) if height > 0 else 0
    if width == 0:
        raise HTTPException(status_code=400, detail="fields must be non-empty grids")

    field_container = MultiCompoundField(width=width, height=height)
    for name, grid in payload.fields.items():
        diffusion_rate = payload.diffusion_rates.get(name)
        if diffusion_rate is None:
            raise HTTPException(status_code=400, detail=f"Missing diffusion rate for {name}")
        decay_rate = (payload.decay_rates or {}).get(name, 0.0)
        field = ChemicalField(name=name, diffusion_rate=diffusion_rate, decay_rate=decay_rate)
        field.grid = np.array(grid, dtype=np.float32)
        field_container.fields[name] = field

    system = ReactionDiffusionSystem(field_container, MetabolicPathway())
    updated = system.step(payload.dt, payload.reaction_params)
    serialized = {name: grid.tolist() for name, grid in updated.items()}
    return ChemicalStepResponse(fields=serialized)
"""FastAPI service for Petri Dish chemical simulation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from chemical.diffusion import ChemicalField, MultiCompoundField
from chemical.metabolism import MetabolicPathway
from chemical.reactions import ReactionDiffusionSystem

app = FastAPI(title="Petri Dish Sim", version="0.1.0")


class ChemicalStepRequest(BaseModel):
    fields: Dict[str, List[List[float]]]
    diffusion_rates: Dict[str, float]
    dt: float = Field(gt=0)
    decay_rates: Optional[Dict[str, float]] = None
    reaction_params: Dict[str, Dict[str, float]]


class ChemicalStepResponse(BaseModel):
    fields: Dict[str, List[List[float]]]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "healthy"}


@app.post("/chemical/step", response_model=ChemicalStepResponse)
async def chemical_step(payload: ChemicalStepRequest) -> ChemicalStepResponse:
    if not payload.fields:
        raise HTTPException(status_code=400, detail="fields must not be empty")

    first_field = next(iter(payload.fields.values()))
    height = len(first_field)
    width = len(first_field[0]) if height > 0 else 0
    if width == 0:
        raise HTTPException(status_code=400, detail="fields must be non-empty grids")

    field_container = MultiCompoundField(width=width, height=height)
    for name, grid in payload.fields.items():
        diffusion_rate = payload.diffusion_rates.get(name)
        if diffusion_rate is None:
            raise HTTPException(status_code=400, detail=f"Missing diffusion rate for {name}")
        decay_rate = (payload.decay_rates or {}).get(name, 0.0)
        field = ChemicalField(name=name, diffusion_rate=diffusion_rate, decay_rate=decay_rate)
        field.grid = np.array(grid, dtype=np.float32)
        field_container.fields[name] = field

    system = ReactionDiffusionSystem(field_container, MetabolicPathway())
    updated = system.step(payload.dt, payload.reaction_params)
    serialized = {name: grid.tolist() for name, grid in updated.items()}
    return ChemicalStepResponse(fields=serialized)
