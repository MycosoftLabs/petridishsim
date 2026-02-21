"""Multi-compound 2D diffusion using finite differences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

try:
    from numba import njit
except Exception:  # pragma: no cover - numba optional at runtime
    njit = None


def _diffuse_step_numpy(grid: np.ndarray, diffusion_rate: float, dt: float) -> np.ndarray:
    padded = np.pad(grid, 1, mode="edge")
    center = padded[1:-1, 1:-1]
    laplacian = (
        padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        - 4.0 * center
    )
    updated = center + diffusion_rate * dt * laplacian
    return np.maximum(updated, 0.0)


if njit:

    @njit(cache=True)
    def _diffuse_step_numba(grid: np.ndarray, diffusion_rate: float, dt: float) -> np.ndarray:
        height, width = grid.shape
        updated = np.empty_like(grid)
        for y in range(height):
            y_up = 0 if y == 0 else y - 1
            y_down = height - 1 if y == height - 1 else y + 1
            for x in range(width):
                x_left = 0 if x == 0 else x - 1
                x_right = width - 1 if x == width - 1 else x + 1
                center = grid[y, x]
                laplacian = (
                    grid[y_up, x]
                    + grid[y_down, x]
                    + grid[y, x_left]
                    + grid[y, x_right]
                    - 4.0 * center
                )
                value = center + diffusion_rate * dt * laplacian
                updated[y, x] = value if value > 0.0 else 0.0
        return updated

else:
    _diffuse_step_numba = None


@dataclass
class ChemicalField:
    name: str
    diffusion_rate: float
    decay_rate: float = 0.0
    grid: np.ndarray | None = None

    def initialize(self, width: int, height: int, initial_value: float = 0.0) -> None:
        self.grid = np.full((height, width), initial_value, dtype=np.float32)

    def step(self, dt: float) -> np.ndarray:
        if self.grid is None:
            raise ValueError(f"ChemicalField '{self.name}' is not initialized.")
        if _diffuse_step_numba:
            updated = _diffuse_step_numba(self.grid, self.diffusion_rate, dt)
        else:
            updated = _diffuse_step_numpy(self.grid, self.diffusion_rate, dt)
        if self.decay_rate > 0:
            updated = np.maximum(updated - self.decay_rate * dt, 0.0)
        self.grid = updated
        return updated


class MultiCompoundField:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.fields: Dict[str, ChemicalField] = {}

    def add_field(self, field: ChemicalField, initial_value: float = 0.0) -> None:
        field.initialize(self.width, self.height, initial_value)
        self.fields[field.name] = field

    def step_all(self, dt: float) -> Dict[str, np.ndarray]:
        return {name: field.step(dt) for name, field in self.fields.items()}
