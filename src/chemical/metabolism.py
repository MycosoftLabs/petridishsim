"""Metabolic pathway computations for growth simulation."""

from __future__ import annotations

from typing import Dict


class MetabolicPathway:
    def glycolysis(
        self,
        glucose_level: float,
        enzyme_activity: float,
        params: Dict[str, float],
    ) -> Dict[str, float]:
        max_uptake = params["max_glucose_uptake"]
        atp_yield = params["atp_yield"]
        uptake = min(glucose_level, max_uptake * enzyme_activity)
        return {
            "glucose_consumed": uptake,
            "pyruvate_produced": uptake,
            "atp_produced": uptake * atp_yield,
        }

    def tca_cycle(
        self,
        pyruvate_level: float,
        oxygen_available: float,
        params: Dict[str, float],
    ) -> Dict[str, float]:
        max_uptake = params["max_pyruvate_uptake"]
        aerobic_atp_yield = params["aerobic_atp_yield"]
        anaerobic_atp_yield = params["anaerobic_atp_yield"]
        uptake = min(pyruvate_level, max_uptake)
        if oxygen_available > 0:
            return {
                "pyruvate_consumed": uptake,
                "co2_produced": uptake,
                "atp_produced": uptake * aerobic_atp_yield,
                "anaerobic_byproduct": 0.0,
            }
        return {
            "pyruvate_consumed": uptake,
            "co2_produced": 0.0,
            "atp_produced": uptake * anaerobic_atp_yield,
            "anaerobic_byproduct": uptake,
        }

    def amino_acid_synthesis(
        self,
        nitrogen_source: float,
        carbon_source: float,
        params: Dict[str, float],
    ) -> Dict[str, float]:
        nitrogen_yield = params["nitrogen_yield"]
        carbon_yield = params["carbon_yield"]
        max_rate = params["max_synthesis_rate"]
        potential = min(nitrogen_source * nitrogen_yield, carbon_source * carbon_yield)
        produced = min(potential, max_rate)
        return {
            "amino_acids_produced": produced,
            "nitrogen_consumed": produced / max(nitrogen_yield, 1e-6),
            "carbon_consumed": produced / max(carbon_yield, 1e-6),
        }

    def protein_synthesis(
        self,
        amino_acid_pool: float,
        energy_available: float,
        params: Dict[str, float],
    ) -> Dict[str, float]:
        aa_per_biomass = params["aa_per_biomass"]
        energy_per_biomass = params["energy_per_biomass"]
        biomass_from_aa = amino_acid_pool / max(aa_per_biomass, 1e-6)
        biomass_from_energy = energy_available / max(energy_per_biomass, 1e-6)
        biomass = min(biomass_from_aa, biomass_from_energy)
        return {
            "biomass_produced": biomass,
            "amino_acids_consumed": biomass * aa_per_biomass,
            "energy_consumed": biomass * energy_per_biomass,
        }
