# Benchmarks

This directory contains benchmark scripts for comparing `grasscalc` against other Grassmannian manifold libraries.

## Quick Start

```bash
# Run benchmarks (grasscalc only)
python benchmarks/benchmark_suite.py

# Run with comparison libraries
pip install geomstats pymanopt autograd
python benchmarks/benchmark_suite.py

# Custom dimensions
python benchmarks/benchmark_suite.py -k 10 -n 50 --trials 200
```

## Benchmarked Operations

| Operation | Description |
|-----------|-------------|
| `random_sample` | Generate random point on Gr(k,n) |
| `geodesic_distance` | Compute Riemannian distance |
| `exp_map` | Exponential map (move along geodesic) |
| `log_map` | Logarithm map (find tangent vector) |
| `parallel_transport` | Transport tangent vector along geodesic |

## Compared Libraries

### grasscalc
- Pure NumPy implementation
- Optimized for research use cases
- Optional GPU backends (PyTorch, JAX)

### geomstats
- General differential geometry library
- Supports many manifolds
- NumPy/PyTorch/TensorFlow backends
- Install: `pip install geomstats`

### pymanopt
- Manifold optimization library
- Focus on optimization algorithms
- Autodiff support
- Install: `pip install pymanopt autograd`

## Example Output

```
======================================================================
Grassmannian Benchmark Suite: Gr(5, 20)
Trials per operation: 100
======================================================================

Available libraries:
  - grasscalc: YES
  - geomstats: YES
  - pymanopt: YES

======================================================================
RESULTS
======================================================================
Library      | Operation                 | Mean ± Std
----------------------------------------------------------------------
grasscalc    | random_sample             |    0.045 ms ±  0.012 ms
geomstats    | random_sample             |    0.089 ms ±  0.021 ms
pymanopt     | random_sample             |    0.067 ms ±  0.018 ms
----------------------------------------------------------------------
grasscalc    | geodesic_distance         |    0.112 ms ±  0.015 ms
geomstats    | geodesic_distance         |    0.245 ms ±  0.034 ms
pymanopt     | geodesic_distance         |    0.198 ms ±  0.028 ms
----------------------------------------------------------------------
...

SPEEDUP vs grasscalc (>1 means grasscalc is faster)
--------------------------------------------------

geomstats:
  random_sample            :  1.98x 🚀
  geodesic_distance        :  2.19x 🚀
  exp_map                  :  1.87x 🚀
  log_map                  :  2.04x 🚀
  parallel_transport       :  1.76x 🚀
```

## GPU Benchmarks

To benchmark GPU performance:

```python
from grasscalc.backends import set_backend

# PyTorch GPU
set_backend('torch', device='cuda')

# JAX (auto-selects GPU if available)
set_backend('jax')
```

## Adding Custom Benchmarks

See `benchmark_suite.py` for the benchmark framework. Add new benchmarks by:

1. Creating a method in the appropriate benchmark class
2. Adding it to `run_all()`
3. Running with appropriate trial count
