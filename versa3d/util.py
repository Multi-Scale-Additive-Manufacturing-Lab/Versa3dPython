__author__ = "Marc Wang"
__copyright__ = "Copyright (c) 2021 Marc Wang"
__license__ = "BSD-3-Clause"
__maintainer__ = "Marc Wang"
__email__ = "marc.wang@uwaterloo.ca"


import numpy as np


def compute_spacing(layer_thickness: float, xy_resolution: float) -> np.ndarray:
    """[summary]

    Args:
        layer_thickness (float): layer thickness in mm
        xy_resolution (float): xy resolution in dpi

    Returns:
        np.array: [description]
    """
    spacing = np.zeros(3, dtype=float)
    spacing[0:2] = 25.4 / xy_resolution
    spacing[2] = np.min(layer_thickness)
    return spacing


def compute_dim(bounds: np.ndarray, spacing: np.ndarray) -> np.ndarray:
    """[summary]

    Args:
        bounds (np.array): dim = 6, vtkpolydata bounds
        spacing (np.array): dim = 3, voxel spacing

    Returns:
        np.array: return img dimenstion
    """
    return np.ceil((bounds[1::2] - bounds[0::2]) / spacing).astype(int)
