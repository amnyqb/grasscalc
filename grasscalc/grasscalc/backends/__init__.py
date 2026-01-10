"""
GPU Backend Support for grasscalc.

This module provides optional backends for GPU acceleration:
- PyTorch: For GPU-accelerated tensor operations
- JAX: For JIT compilation and automatic differentiation

Usage
-----
>>> from grasscalc.backends import get_backend, set_backend
>>> set_backend('torch')  # or 'jax' or 'numpy'
>>>
>>> # Operations will now use the selected backend
>>> from grasscalc.core.random import sample_grassmann
>>> U = sample_grassmann(3, 7)  # Uses PyTorch tensors on GPU if available

Backend Selection
-----------------
- 'numpy': Default, CPU-only (always available)
- 'torch': PyTorch backend (requires torch package)
- 'jax': JAX backend (requires jax package)
"""

from .base import (
    get_backend,
    set_backend,
    get_available_backends,
    Backend,
    NumpyBackend,
)

# Conditional imports
try:
    from .torch_backend import TorchBackend
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from .jax_backend import JAXBackend
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

__all__ = [
    'get_backend',
    'set_backend',
    'get_available_backends',
    'Backend',
    'NumpyBackend',
    'TORCH_AVAILABLE',
    'JAX_AVAILABLE',
]

if TORCH_AVAILABLE:
    __all__.append('TorchBackend')

if JAX_AVAILABLE:
    __all__.append('JAXBackend')
