"""Morphological statistics extraction for mycelium masks."""

from __future__ import annotations

from typing import Dict

import numpy as np
from scipy import ndimage


def network_coverage(mask: np.ndarray) -> float:
    return float(np.sum(mask > 0) / mask.size)


def measure_hyphal_length(mask: np.ndarray) -> float:
    return float(np.sum(mask > 0))


def count_branch_points(mask: np.ndarray) -> int:
    binary = (mask > 0).astype(np.uint8)
    kernel = np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ],
        dtype=np.uint8,
    )
    neighbor_count = ndimage.convolve(binary, kernel, mode="constant", cval=0)
    return int(np.sum((binary == 1) & (neighbor_count >= 3)))


def measure_average_thickness(mask: np.ndarray) -> float:
    binary = mask > 0
    if not np.any(binary):
        return 0.0
    distances = ndimage.distance_transform_edt(binary)
    return float(2 * np.mean(distances[binary]))


def detect_sclerotia(mask: np.ndarray, min_area: int = 0) -> int:
    labeled, num = ndimage.label(mask > 0)
    if num == 0:
        return 0
    counts = np.bincount(labeled.ravel())
    return int(np.sum(counts[1:] > min_area))


def extract_morphology(mask: np.ndarray, min_sclerotia_area: int = 0) -> Dict[str, float]:
    area = float(np.sum(mask > 0))
    return {
        "hyphal_length": measure_hyphal_length(mask),
        "branching_density": (count_branch_points(mask) / area) if area > 0 else 0.0,
        "network_coverage": network_coverage(mask),
        "filament_thickness": measure_average_thickness(mask),
        "sclerotia_count": float(detect_sclerotia(mask, min_sclerotia_area)),
    }
"""Morphological statistics extraction for mycelium masks."""

from __future__ import annotations

from typing import Dict

import numpy as np
from scipy import ndimage


def network_coverage(mask: np.ndarray) -> float:
    return float(np.sum(mask > 0) / mask.size)


def measure_hyphal_length(mask: np.ndarray) -> float:
    return float(np.sum(mask > 0))


def count_branch_points(mask: np.ndarray) -> int:
    binary = (mask > 0).astype(np.uint8)
    kernel = np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ],
        dtype=np.uint8,
    )
    neighbor_count = ndimage.convolve(binary, kernel, mode="constant", cval=0)
    return int(np.sum((binary == 1) & (neighbor_count >= 3)))


def measure_average_thickness(mask: np.ndarray) -> float:
    binary = mask > 0
    if not np.any(binary):
        return 0.0
    distances = ndimage.distance_transform_edt(binary)
    return float(2 * np.mean(distances[binary]))


def detect_sclerotia(mask: np.ndarray, min_area: int = 0) -> int:
    labeled, num = ndimage.label(mask > 0)
    if num == 0:
        return 0
    counts = np.bincount(labeled.ravel())
    return int(np.sum(counts[1:] > min_area))


def extract_morphology(mask: np.ndarray, min_sclerotia_area: int = 0) -> Dict[str, float]:
    area = float(np.sum(mask > 0))
    return {
        "hyphal_length": measure_hyphal_length(mask),
        "branching_density": (count_branch_points(mask) / area) if area > 0 else 0.0,
        "network_coverage": network_coverage(mask),
        "filament_thickness": measure_average_thickness(mask),
        "sclerotia_count": float(detect_sclerotia(mask, min_sclerotia_area)),
    }
