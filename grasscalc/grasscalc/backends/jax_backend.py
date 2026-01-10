"""
JAX backend for JIT-compiled Grassmannian computations.
"""

from typing import Any, Optional, Tuple, Union
import numpy as np

try:
    import jax
    import jax.numpy as jnp
    from jax import random as jax_random
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    raise ImportError("JAX is required for jax_backend")

from .base import Backend


class JAXBackend(Backend):
    """
    JAX backend for JIT compilation and automatic differentiation.

    JAX provides:
    - Just-in-time (JIT) compilation for faster execution
    - Automatic differentiation (grad, jacobian, hessian)
    - GPU/TPU acceleration
    - Functional programming style

    Examples
    --------
    >>> from grasscalc.backends import set_backend
    >>> backend = set_backend('jax')
    >>>
    >>> # Operations can be JIT-compiled
    >>> import jax
    >>> @jax.jit
    >>> def fast_operation(U, V):
    ...     return backend.matmul(backend.transpose(U), V)
    """

    def __init__(self, dtype=None):
        if not JAX_AVAILABLE:
            raise ImportError("JAX not installed")

        self._dtype = dtype or jnp.float64
        self._key = jax_random.PRNGKey(0)

        # Enable 64-bit precision by default
        jax.config.update("jax_enable_x64", True)

    @property
    def name(self) -> str:
        return 'jax'

    @property
    def device(self) -> str:
        # JAX automatically selects the best device
        devices = jax.devices()
        if devices:
            return str(devices[0].device_kind)
        return 'cpu'

    def array(self, data: Any, dtype: Optional[Any] = None) -> jnp.ndarray:
        return jnp.array(data, dtype=dtype or self._dtype)

    def zeros(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> jnp.ndarray:
        return jnp.zeros(shape, dtype=dtype or self._dtype)

    def ones(self, shape: Tuple[int, ...], dtype: Optional[Any] = None) -> jnp.ndarray:
        return jnp.ones(shape, dtype=dtype or self._dtype)

    def eye(self, n: int, dtype: Optional[Any] = None) -> jnp.ndarray:
        return jnp.eye(n, dtype=dtype or self._dtype)

    def randn(self, *shape: int, rng: Optional[Any] = None) -> jnp.ndarray:
        if rng is not None and hasattr(rng, 'standard_normal'):
            # Convert numpy rng output
            data = rng.standard_normal(shape)
            return jnp.array(data, dtype=self._dtype)
        # Use internal JAX random key
        self._key, subkey = jax_random.split(self._key)
        return jax_random.normal(subkey, shape, dtype=self._dtype)

    def to_numpy(self, arr: jnp.ndarray) -> np.ndarray:
        return np.array(arr)

    def from_numpy(self, arr: np.ndarray) -> jnp.ndarray:
        return jnp.array(arr, dtype=self._dtype)

    def matmul(self, a: jnp.ndarray, b: jnp.ndarray) -> jnp.ndarray:
        return jnp.matmul(a, b)

    def transpose(self, a: jnp.ndarray) -> jnp.ndarray:
        return a.T

    def qr(self, a: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
        return jnp.linalg.qr(a)

    def svd(self, a: jnp.ndarray, full_matrices: bool = False) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
        return jnp.linalg.svd(a, full_matrices=full_matrices)

    def eigh(self, a: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
        return jnp.linalg.eigh(a)

    def norm(self, a: jnp.ndarray, ord: Optional[str] = None) -> jnp.ndarray:
        if ord == 'fro':
            return jnp.linalg.norm(a, ord='fro')
        return jnp.linalg.norm(a)

    def trace(self, a: jnp.ndarray) -> jnp.ndarray:
        return jnp.trace(a)

    def diag(self, a: jnp.ndarray) -> jnp.ndarray:
        return jnp.diag(a)

    def sin(self, a: jnp.ndarray) -> jnp.ndarray:
        return jnp.sin(a)

    def cos(self, a: jnp.ndarray) -> jnp.ndarray:
        return jnp.cos(a)

    def arccos(self, a: jnp.ndarray) -> jnp.ndarray:
        return jnp.arccos(a)

    def sqrt(self, a: jnp.ndarray) -> jnp.ndarray:
        return jnp.sqrt(a)

    def abs(self, a: jnp.ndarray) -> jnp.ndarray:
        return jnp.abs(a)

    def clip(self, a: jnp.ndarray, min_val: float, max_val: float) -> jnp.ndarray:
        return jnp.clip(a, min_val, max_val)

    def sum(self, a: jnp.ndarray, axis: Optional[int] = None) -> Union[jnp.ndarray, float]:
        return jnp.sum(a, axis=axis)

    def stack(self, arrays: list, axis: int = 0) -> jnp.ndarray:
        return jnp.stack(arrays, axis=axis)

    # Additional JAX-specific methods
    def jit(self, fn):
        """JIT-compile a function."""
        return jax.jit(fn)

    def grad(self, fn, argnums: int = 0):
        """Get gradient function."""
        return jax.grad(fn, argnums=argnums)

    def value_and_grad(self, fn, argnums: int = 0):
        """Get function that returns both value and gradient."""
        return jax.value_and_grad(fn, argnums=argnums)

    def hessian(self, fn, argnums: int = 0):
        """Get Hessian function."""
        return jax.hessian(fn, argnums=argnums)

    def jacobian(self, fn, argnums: int = 0):
        """Get Jacobian function."""
        return jax.jacfwd(fn, argnums=argnums)

    def vmap(self, fn, in_axes=0, out_axes=0):
        """Vectorized map over batch dimension."""
        return jax.vmap(fn, in_axes=in_axes, out_axes=out_axes)

    def pmap(self, fn, axis_name='batch'):
        """Parallel map across devices."""
        return jax.pmap(fn, axis_name=axis_name)

    def set_random_key(self, seed: int):
        """Set random key from seed."""
        self._key = jax_random.PRNGKey(seed)
