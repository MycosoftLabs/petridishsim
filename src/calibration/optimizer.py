"""Parameter fitting for Petri Dish Simulator calibration."""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np
from scipy.optimize import minimize


SimulationFn = Callable[[Dict[str, float]], np.ndarray]
MetricFn = Callable[[np.ndarray, np.ndarray], float]


def calibrate_species(
    species_name: str,
    samples: List[np.ndarray],
    simulate_fn: SimulationFn,
    metric_fn: MetricFn,
    initial_params: Dict[str, float],
    bounds: Dict[str, Tuple[float, float]],
    max_iter: int = 50,
) -> Dict[str, float]:
    keys = list(initial_params.keys())

    def objective(values: np.ndarray) -> float:
        params = {key: float(values[i]) for i, key in enumerate(keys)}
        scores = []
        for sample in samples:
            simulated = simulate_fn(params)
            scores.append(metric_fn(simulated, sample))
        return float(np.mean(scores))

    x0 = np.array([initial_params[key] for key in keys], dtype=np.float32)
    bound_list = [bounds[key] for key in keys]

    result = minimize(
        objective,
        x0,
        bounds=bound_list,
        options={"maxiter": max_iter},
    )

    return {key: float(result.x[i]) for i, key in enumerate(keys)}
"""Parameter fitting for Petri Dish Simulator calibration."""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np
from scipy.optimize import minimize


SimulationFn = Callable[[Dict[str, float]], np.ndarray]
MetricFn = Callable[[np.ndarray, np.ndarray], float]


def calibrate_species(
    species_name: str,
    samples: List[np.ndarray],
    simulate_fn: SimulationFn,
    metric_fn: MetricFn,
    initial_params: Dict[str, float],
    bounds: Dict[str, Tuple[float, float]],
    max_iter: int = 50,
) -> Dict[str, float]:
    keys = list(initial_params.keys())

    def objective(values: np.ndarray) -> float:
        params = {key: float(values[i]) for i, key in enumerate(keys)}
        scores = []
        for sample in samples:
            simulated = simulate_fn(params)
            scores.append(metric_fn(simulated, sample))
        return float(np.mean(scores))

    x0 = np.array([initial_params[key] for key in keys], dtype=np.float32)
    bound_list = [bounds[key] for key in keys]

    result = minimize(
        objective,
        x0,
        bounds=bound_list,
        options={"maxiter": max_iter},
    )

    return {key: float(result.x[i]) for i, key in enumerate(keys)}
