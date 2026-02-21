"""Reaction-diffusion coupling between fields and metabolism."""

from __future__ import annotations

from typing import Dict, Optional, Union

import numpy as np

from .diffusion import MultiCompoundField
from .metabolism import MetabolicPathway


ScalarOrGrid = Union[float, np.ndarray]


class ReactionDiffusionSystem:
    def __init__(self, fields: MultiCompoundField, metabolism: MetabolicPathway):
        self.fields = fields
        self.metabolism = metabolism

    def _grid(self, name: str) -> Optional[np.ndarray]:
        field = self.fields.fields.get(name)
        return None if field is None else field.grid

    def _value(self, value: ScalarOrGrid, y: int, x: int) -> float:
        if isinstance(value, np.ndarray):
            return float(value[y, x])
        return float(value)

    def step(self, dt: float, reaction_params: Dict[str, Dict[str, float]]) -> Dict[str, np.ndarray]:
        self.fields.step_all(dt)

        glucose = self._grid("glucose")
        pyruvate = self._grid("pyruvate")
        amino_acids = self._grid("amino_acids")
        atp = self._grid("atp")
        biomass = self._grid("biomass")
        oxygen = self._grid("oxygen")
        co2 = self._grid("co2")
        anaerobic_byproduct = self._grid("anaerobic_byproduct")

        if glucose is None:
            return {name: field.grid for name, field in self.fields.fields.items()}

        height, width = glucose.shape
        enzyme_activity = reaction_params.get("enzyme_activity", 1.0)

        for y in range(height):
            for x in range(width):
                glyco = self.metabolism.glycolysis(
                    glucose[y, x],
                    self._value(enzyme_activity, y, x),
                    reaction_params["glycolysis"],
                )
                glucose[y, x] = max(glucose[y, x] - glyco["glucose_consumed"], 0.0)
                if pyruvate is not None:
                    pyruvate[y, x] += glyco["pyruvate_produced"]
                if atp is not None:
                    atp[y, x] += glyco["atp_produced"]

                if pyruvate is None:
                    continue

                oxygen_available = oxygen[y, x] if oxygen is not None else 0.0
                tca = self.metabolism.tca_cycle(
                    pyruvate[y, x],
                    oxygen_available,
                    reaction_params["tca_cycle"],
                )
                pyruvate[y, x] = max(pyruvate[y, x] - tca["pyruvate_consumed"], 0.0)
                if oxygen is not None and oxygen_available > 0:
                    oxygen[y, x] = max(oxygen[y, x] - tca["pyruvate_consumed"], 0.0)
                if atp is not None:
                    atp[y, x] += tca["atp_produced"]
                if co2 is not None:
                    co2[y, x] += tca["co2_produced"]
                if anaerobic_byproduct is not None:
                    anaerobic_byproduct[y, x] += tca["anaerobic_byproduct"]

                if amino_acids is None:
                    continue

                aa = self.metabolism.amino_acid_synthesis(
                    nitrogen_source=amino_acids[y, x],
                    carbon_source=glucose[y, x],
                    params=reaction_params["amino_acid_synthesis"],
                )
                amino_acids[y, x] += aa["amino_acids_produced"]

                if biomass is None or atp is None:
                    continue

                protein = self.metabolism.protein_synthesis(
                    amino_acids[y, x],
                    atp[y, x],
                    reaction_params["protein_synthesis"],
                )
                biomass[y, x] += protein["biomass_produced"]
                amino_acids[y, x] = max(amino_acids[y, x] - protein["amino_acids_consumed"], 0.0)
                atp[y, x] = max(atp[y, x] - protein["energy_consumed"], 0.0)

        return {name: field.grid for name, field in self.fields.fields.items()}
