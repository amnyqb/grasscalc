"""
Base backend interface for grasscalc.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, Union
import numpy as np

# Global backend state
_current_backend = None


class Backend(ABC):
    """Abstract base class for backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend name."""
        pass

    @property
    @abstractmethod
    def device(self) -> str:
        """Current device (cpu/cuda)."""
        pass

    @abstractmethod
    def array(self, data: Any, dtype: Optional[Any] = None) -> Any:
        """Create an array from data."""
        pass

    @abstractmethod
    def zeros(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> Any:
        """Create zeros array."""
        pass

    @abstractmethod
    def ones(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> Any:
        """Create ones array."""
        pass

    @abstractmethod
    def eye(self, n: int, dtype: Optional[Any] = None) -> Any:
        """Create identity matrix."""
        pass

    @abstractmethod
    def randn(self, *shape: int, rng: Optional[Any] = None) -> Any:
        """Create standard normal random array."""
        pass

    @abstractmethod
    def to_numpy(self, arr: Any) -> np.ndarray:
        """Convert backend array to numpy."""
        pass

    @abstractmethod
    def from_numpy(self, arr: np.ndarray) -> Any:
        """Convert numpy array to backend type."""
        pass

    # Linear algebra operations
    @abstractmethod
    def matmul(self, a: Any, b: Any) -> Any:
        """Matrix multiplication."""
        pass

    @abstractmethod
    def transpose(self, a: Any) -> Any:
        """Transpose (swap last two dimensions)."""
        pass

    @abstractmethod
    def qr(self, a: Any) -> Tuple[Any, Any]:
        """QR decomposition."""
        pass

    @abstractmethod
    def svd(self, a: Any, full_matrices: bool = False) -> Tuple[Any, Any, Any]:
        """SVD decomposition."""
        pass

    @abstractmethod
    def eigh(self, a: Any) -> Tuple[Any, Any]:
        """Eigendecomposition of symmetric/Hermitian matrix."""
        pass

    @abstractmethod
    def norm(self, a: Any, ord: Optional[str] = None) -> Any:
        """Matrix or vector norm."""
        pass

    @abstractmethod
    def trace(self, a: Any) -> Any:
        """Matrix trace."""
        pass

    @abstractmethod
    def diag(self, a: Any) -> Any:
        """Extract diagonal or create diagonal matrix."""
        pass

    # Trigonometric operations (for exp/log maps)
    @abstractmethod
    def sin(self, a: Any) -> Any:
        """Element-wise sine."""
        pass

    @abstractmethod
    def cos(self, a: Any) -> Any:
        """Element-wise cosine."""
        pass

    @abstractmethod
    def arccos(self, a: Any) -> Any:
        """Element-wise arccosine."""
        pass

    @abstractmethod
    def sqrt(self, a: Any) -> Any:
        """Element-wise square root."""
        pass

    @abstractmethod
    def abs(self, a: Any) -> Any:
        """Element-wise absolute value."""
        pass

    @abstractmethod
    def clip(self, a: Any, min_val: float, max_val: float) -> Any:
        """Clip values to range."""
        pass

    @abstractmethod
    def sum(self, a: Any, axis: Optional[int] = None) -> Any:
        """Sum of array elements."""
        pass

    @abstractmethod
    def stack(self, arrays: list, axis: int = 0) -> Any:
        """Stack arrays along new axis."""
        pass


class NumpyBackend(Backend):
    """NumPy backend (default, CPU-only)."""

    @property
    def name(self) -> str:
        return 'numpy'

    @property
    def device(self) -> str:
        return 'cpu'

    def array(self, data: Any, dtype: Optional[Any] = None) -> np.ndarray:
        return np.array(data, dtype=dtype or np.float64)

    def zeros(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> np.ndarray:
        return np.zeros(shape, dtype=dtype or np.float64)

    def ones(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> np.ndarray:
        return np.ones(shape, dtype=dtype or np.float64)

    def eye(self, n: int, dtype: Optional[Any] = None) -> np.ndarray:
        return np.eye(n, dtype=dtype or np.float64)

    def randn(self, *shape: int, rng: Optional[Any] = None) -> np.ndarray:
        if rng is None:
            rng = np.random.default_rng()
        return rng.standard_normal(shape)

    def to_numpy(self, arr: np.ndarray) -> np.ndarray:
        return arr

    def from_numpy(self, arr: np.ndarray) -> np.ndarray:
        return arr.copy()

    def matmul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return a @ b

    def transpose(self, a: np.ndarray) -> np.ndarray:
        return a.T

    def qr(self, a: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return np.linalg.qr(a)

    def svd(self, a: np.ndarray, full_matrices: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return np.linalg.svd(a, full_matrices=full_matrices)

    def eigh(self, a: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return np.linalg.eigh(a)

    def norm(self, a: np.ndarray, ord: Optional[str] = None) -> float:
        if ord == 'fro':
            return np.linalg.norm(a, ord='fro')
        return np.linalg.norm(a)

    def trace(self, a: np.ndarray) -> float:
        return np.trace(a)

    def diag(self, a: np.ndarray) -> np.ndarray:
        return np.diag(a)

    def sin(self, a: np.ndarray) -> np.ndarray:
        return np.sin(a)

    def cos(self, a: np.ndarray) -> np.ndarray:
        return np.cos(a)

    def arccos(self, a: np.ndarray) -> np.ndarray:
        return np.arccos(a)

    def sqrt(self, a: np.ndarray) -> np.ndarray:
        return np.sqrt(a)

    def abs(self, a: np.ndarray) -> np.ndarray:
        return np.abs(a)

    def clip(self, a: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
        return np.clip(a, min_val, max_val)

    def sum(self, a: np.ndarray, axis: Optional[int] = None) -> Union[float, np.ndarray]:
        return np.sum(a, axis=axis)

    def stack(self, arrays: list, axis: int = 0) -> np.ndarray:
        return np.stack(arrays, axis=axis)


# Default backend
_numpy_backend = NumpyBackend()
_current_backend = _numpy_backend


def get_backend() -> Backend:
    """Get the current backend."""
    global _current_backend
    if _current_backend is None:
        _current_backend = _numpy_backend
    return _current_backend


def set_backend(name: str, device: str = 'cpu') -> Backend:
    """
    Set the current backend.

    Parameters
    ----------
    name : str
        Backend name: 'numpy', 'torch', or 'jax'
    device : str
        Device for GPU backends: 'cpu' or 'cuda'

    Returns
    -------
    Backend
        The new active backend
    """
    global _current_backend

    if name == 'numpy':
        _current_backend = _numpy_backend

    elif name == 'torch':
        try:
            from .torch_backend import TorchBackend
            _current_backend = TorchBackend(device=device)
        except ImportError:
            raise ImportError(
                "PyTorch not installed. Install with: pip install torch"
            )

    elif name == 'jax':
        try:
            from .jax_backend import JAXBackend
            _current_backend = JAXBackend()
        except ImportError:
            raise ImportError(
                "JAX not installed. Install with: pip install jax jaxlib"
            )

    else:
        raise ValueError(f"Unknown backend: {name}")

    return _current_backend


def get_available_backends() -> list:
    """Get list of available backend names."""
    backends = ['numpy']

    try:
        import torch
        backends.append('torch')
    except ImportError:
        pass

    try:
        import jax
        backends.append('jax')
    except ImportError:
        pass

    return backends
