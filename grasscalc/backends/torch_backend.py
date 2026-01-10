"""
PyTorch backend for GPU-accelerated Grassmannian computations.
"""

from typing import Any, Optional, Tuple, Union
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    raise ImportError("PyTorch is required for torch_backend")

from .base import Backend


class TorchBackend(Backend):
    """
    PyTorch backend for GPU acceleration.

    Parameters
    ----------
    device : str
        Device to use: 'cpu', 'cuda', or 'cuda:0', etc.
    dtype : torch.dtype
        Default tensor dtype

    Examples
    --------
    >>> from grasscalc.backends import set_backend
    >>> backend = set_backend('torch', device='cuda')
    >>> print(backend.device)
    cuda
    """

    def __init__(self, device: str = 'cpu', dtype=None):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not installed")

        self._device = torch.device(device)
        self._dtype = dtype or torch.float64

        # Check if CUDA is available when requested
        if 'cuda' in device and not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU")
            self._device = torch.device('cpu')

    @property
    def name(self) -> str:
        return 'torch'

    @property
    def device(self) -> str:
        return str(self._device)

    def array(self, data: Any, dtype: Optional[Any] = None) -> torch.Tensor:
        if isinstance(data, torch.Tensor):
            return data.to(device=self._device, dtype=dtype or self._dtype)
        return torch.tensor(data, device=self._device, dtype=dtype or self._dtype)

    def zeros(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> torch.Tensor:
        return torch.zeros(*shape, device=self._device, dtype=dtype or self._dtype)

    def ones(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> torch.Tensor:
        return torch.ones(*shape, device=self._device, dtype=dtype or self._dtype)

    def eye(self, n: int, dtype: Optional[Any] = None) -> torch.Tensor:
        return torch.eye(n, device=self._device, dtype=dtype or self._dtype)

    def randn(self, *shape: int, rng: Optional[Any] = None) -> torch.Tensor:
        # Note: torch doesn't use numpy-style rng, so we use global state or generator
        if rng is not None and hasattr(rng, 'standard_normal'):
            # Convert numpy rng output to tensor
            data = rng.standard_normal(shape)
            return torch.tensor(data, device=self._device, dtype=self._dtype)
        return torch.randn(*shape, device=self._device, dtype=self._dtype)

    def to_numpy(self, arr: torch.Tensor) -> np.ndarray:
        return arr.detach().cpu().numpy()

    def from_numpy(self, arr: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(arr.copy()).to(device=self._device, dtype=self._dtype)

    def matmul(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        return torch.matmul(a, b)

    def transpose(self, a: torch.Tensor) -> torch.Tensor:
        return a.T

    def qr(self, a: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        return torch.linalg.qr(a)

    def svd(self, a: torch.Tensor, full_matrices: bool = False) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return torch.linalg.svd(a, full_matrices=full_matrices)

    def eigh(self, a: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        return torch.linalg.eigh(a)

    def norm(self, a: torch.Tensor, ord: Optional[str] = None) -> torch.Tensor:
        if ord == 'fro':
            return torch.linalg.norm(a, ord='fro')
        return torch.linalg.norm(a)

    def trace(self, a: torch.Tensor) -> torch.Tensor:
        return torch.trace(a)

    def diag(self, a: torch.Tensor) -> torch.Tensor:
        return torch.diag(a)

    def sin(self, a: torch.Tensor) -> torch.Tensor:
        return torch.sin(a)

    def cos(self, a: torch.Tensor) -> torch.Tensor:
        return torch.cos(a)

    def arccos(self, a: torch.Tensor) -> torch.Tensor:
        return torch.acos(a)

    def sqrt(self, a: torch.Tensor) -> torch.Tensor:
        return torch.sqrt(a)

    def abs(self, a: torch.Tensor) -> torch.Tensor:
        return torch.abs(a)

    def clip(self, a: torch.Tensor, min_val: float, max_val: float) -> torch.Tensor:
        return torch.clamp(a, min=min_val, max=max_val)

    def sum(self, a: torch.Tensor, axis: Optional[int] = None) -> Union[torch.Tensor, float]:
        if axis is None:
            return torch.sum(a)
        return torch.sum(a, dim=axis)

    def stack(self, arrays: list, axis: int = 0) -> torch.Tensor:
        return torch.stack(arrays, dim=axis)

    # Additional PyTorch-specific methods
    def requires_grad(self, arr: torch.Tensor, requires: bool = True) -> torch.Tensor:
        """Enable/disable gradient tracking."""
        return arr.requires_grad_(requires)

    def grad(self, output: torch.Tensor, inputs: torch.Tensor) -> torch.Tensor:
        """Compute gradients via autograd."""
        return torch.autograd.grad(output, inputs, create_graph=True)[0]

    def to_device(self, arr: torch.Tensor, device: str) -> torch.Tensor:
        """Move tensor to specified device."""
        return arr.to(torch.device(device))
