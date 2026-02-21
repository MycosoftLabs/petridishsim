"""Enzyme kinetics for chemical simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class EnzymeKinetics:
    vmax: float
    km: float
    decay_rate: float = 0.0


def michaelis_menten(substrate: float, kinetics: EnzymeKinetics) -> float:
    if substrate <= 0:
        return 0.0
    return (kinetics.vmax * substrate) / (kinetics.km + substrate)


class EnzymeSystem:
    def __init__(self, kinetics_map: Dict[str, EnzymeKinetics]):
        self.kinetics_map = kinetics_map

    def laccase_production(self, lignin_level: float) -> float:
        return michaelis_menten(lignin_level, self.kinetics_map["laccase"])

    def xylanase_production(self, hemicellulose_level: float) -> float:
        return michaelis_menten(hemicellulose_level, self.kinetics_map["xylanase"])

    def pectinase_production(self, pectin_level: float) -> float:
        return michaelis_menten(pectin_level, self.kinetics_map["pectinase"])

    def amylase_production(self, starch_level: float) -> float:
        return michaelis_menten(starch_level, self.kinetics_map["amylase"])

    def cellulase_production(self, cellulose_level: float) -> float:
        return michaelis_menten(cellulose_level, self.kinetics_map["cellulase"])

    def apply_decay(self, enzyme_level: float, enzyme_name: str, dt: float) -> float:
        decay = self.kinetics_map[enzyme_name].decay_rate * dt
        return max(enzyme_level - decay, 0.0)
