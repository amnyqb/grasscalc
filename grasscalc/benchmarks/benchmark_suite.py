#!/usr/bin/env python
"""
Benchmark suite for grasscalc comparing against geomstats and pymanopt.

This script benchmarks core Grassmannian operations:
- Random sampling
- Distance computation
- Exponential/Logarithm maps
- Parallel transport
- Gradient descent optimization

Run with: python benchmarks/benchmark_suite.py

Requirements for full comparison:
- pip install grasscalc geomstats pymanopt autograd
"""

import time
import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
import sys

# Try importing optional packages
HAS_GEOMSTATS = False
HAS_PYMANOPT = False

try:
    import geomstats.geometry.grassmannian as geomstats_gr
    from geomstats.geometry.grassmannian import Grassmannian as GeomstatsGrassmannian
    HAS_GEOMSTATS = True
except ImportError:
    pass

try:
    import pymanopt
    from pymanopt.manifolds import Grassmann as PymanoptGrassmann
    HAS_PYMANOPT = True
except ImportError:
    pass


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""
    name: str
    library: str
    n_trials: int
    mean_time: float
    std_time: float
    min_time: float
    max_time: float

    def __str__(self):
        return (f"{self.library:12s} | {self.name:25s} | "
                f"{self.mean_time*1000:8.3f} ms ± {self.std_time*1000:6.3f} ms")


def timeit(fn: Callable, n_trials: int = 100, warmup: int = 5) -> Tuple[float, float, float, float]:
    """
    Time a function over multiple trials.

    Returns: (mean, std, min, max) in seconds
    """
    # Warmup
    for _ in range(warmup):
        fn()

    times = []
    for _ in range(n_trials):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)

    times = np.array(times)
    return times.mean(), times.std(), times.min(), times.max()


class GrasscalcBenchmarks:
    """Benchmarks using grasscalc."""

    def __init__(self, k: int, n: int, rng=None):
        self.k = k
        self.n = n
        self.rng = rng or np.random.default_rng(42)

        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.distances import geodesic_distance, chordal_distance
        from grasscalc.core.tangent import (
            exponential_map, logarithm_map, parallel_transport,
            tangent_project
        )

        self.sample_grassmann = sample_grassmann
        self.geodesic_distance = geodesic_distance
        self.chordal_distance = chordal_distance
        self.exp_map = exponential_map
        self.log_map = logarithm_map
        self.parallel_transport = parallel_transport
        self.tangent_project = tangent_project

    def bench_sample(self, n_trials: int = 100) -> BenchmarkResult:
        def fn():
            return self.sample_grassmann(self.k, self.n, self.rng)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="random_sample",
            library="grasscalc",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_geodesic_distance(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.sample_grassmann(self.k, self.n, self.rng)
        V = self.sample_grassmann(self.k, self.n, self.rng)

        def fn():
            return self.geodesic_distance(U, V)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="geodesic_distance",
            library="grasscalc",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_exp_map(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.sample_grassmann(self.k, self.n, self.rng)
        Xi = self.tangent_project(U, self.rng.standard_normal((self.n, self.k)))

        def fn():
            return self.exp_map(U, Xi)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="exp_map",
            library="grasscalc",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_log_map(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.sample_grassmann(self.k, self.n, self.rng)
        V = self.sample_grassmann(self.k, self.n, self.rng)

        def fn():
            return self.log_map(U, V)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="log_map",
            library="grasscalc",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_parallel_transport(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.sample_grassmann(self.k, self.n, self.rng)
        V = self.sample_grassmann(self.k, self.n, self.rng)
        Xi = self.tangent_project(U, self.rng.standard_normal((self.n, self.k)))

        def fn():
            return self.parallel_transport(U, V, Xi)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="parallel_transport",
            library="grasscalc",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def run_all(self, n_trials: int = 100) -> List[BenchmarkResult]:
        return [
            self.bench_sample(n_trials),
            self.bench_geodesic_distance(n_trials),
            self.bench_exp_map(n_trials),
            self.bench_log_map(n_trials),
            self.bench_parallel_transport(n_trials),
        ]


class GeomstatsBenchmarks:
    """Benchmarks using geomstats."""

    def __init__(self, k: int, n: int, rng=None):
        if not HAS_GEOMSTATS:
            raise ImportError("geomstats not installed")

        self.k = k
        self.n = n
        self.rng = rng or np.random.default_rng(42)
        self.manifold = GeomstatsGrassmannian(n, k)

    def bench_sample(self, n_trials: int = 100) -> BenchmarkResult:
        def fn():
            return self.manifold.random_point()

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="random_sample",
            library="geomstats",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_geodesic_distance(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        V = self.manifold.random_point()

        def fn():
            return self.manifold.metric.dist(U, V)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="geodesic_distance",
            library="geomstats",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_exp_map(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        Xi = self.manifold.random_tangent_vec(U)

        def fn():
            return self.manifold.metric.exp(Xi, U)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="exp_map",
            library="geomstats",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_log_map(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        V = self.manifold.random_point()

        def fn():
            return self.manifold.metric.log(V, U)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="log_map",
            library="geomstats",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_parallel_transport(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        V = self.manifold.random_point()
        Xi = self.manifold.random_tangent_vec(U)

        def fn():
            return self.manifold.metric.parallel_transport(Xi, U, V)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="parallel_transport",
            library="geomstats",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def run_all(self, n_trials: int = 100) -> List[BenchmarkResult]:
        return [
            self.bench_sample(n_trials),
            self.bench_geodesic_distance(n_trials),
            self.bench_exp_map(n_trials),
            self.bench_log_map(n_trials),
            self.bench_parallel_transport(n_trials),
        ]


class PymanoptBenchmarks:
    """Benchmarks using pymanopt."""

    def __init__(self, k: int, n: int, rng=None):
        if not HAS_PYMANOPT:
            raise ImportError("pymanopt not installed")

        self.k = k
        self.n = n
        self.rng = rng or np.random.default_rng(42)
        self.manifold = PymanoptGrassmann(n, k)

    def bench_sample(self, n_trials: int = 100) -> BenchmarkResult:
        def fn():
            return self.manifold.random_point()

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="random_sample",
            library="pymanopt",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_geodesic_distance(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        V = self.manifold.random_point()

        def fn():
            return self.manifold.dist(U, V)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="geodesic_distance",
            library="pymanopt",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_exp_map(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        Xi = self.manifold.random_tangent_vector(U)

        def fn():
            return self.manifold.exp(U, Xi)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="exp_map",
            library="pymanopt",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_log_map(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        V = self.manifold.random_point()

        def fn():
            return self.manifold.log(U, V)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="log_map",
            library="pymanopt",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def bench_parallel_transport(self, n_trials: int = 100) -> BenchmarkResult:
        U = self.manifold.random_point()
        V = self.manifold.random_point()
        Xi = self.manifold.random_tangent_vector(U)

        def fn():
            return self.manifold.transport(U, V, Xi)

        mean, std, min_, max_ = timeit(fn, n_trials)
        return BenchmarkResult(
            name="parallel_transport",
            library="pymanopt",
            n_trials=n_trials,
            mean_time=mean,
            std_time=std,
            min_time=min_,
            max_time=max_
        )

    def run_all(self, n_trials: int = 100) -> List[BenchmarkResult]:
        return [
            self.bench_sample(n_trials),
            self.bench_geodesic_distance(n_trials),
            self.bench_exp_map(n_trials),
            self.bench_log_map(n_trials),
            self.bench_parallel_transport(n_trials),
        ]


def run_comparison(k: int = 5, n: int = 20, n_trials: int = 100):
    """Run full benchmark comparison."""
    print("=" * 70)
    print(f"Grassmannian Benchmark Suite: Gr({k}, {n})")
    print(f"Trials per operation: {n_trials}")
    print("=" * 70)
    print()

    # Available libraries
    print("Available libraries:")
    print(f"  - grasscalc: YES")
    print(f"  - geomstats: {'YES' if HAS_GEOMSTATS else 'NO'}")
    print(f"  - pymanopt:  {'YES' if HAS_PYMANOPT else 'NO'}")
    print()

    all_results = []

    # grasscalc benchmarks
    print("Running grasscalc benchmarks...")
    gc_bench = GrasscalcBenchmarks(k, n)
    all_results.extend(gc_bench.run_all(n_trials))

    # geomstats benchmarks
    if HAS_GEOMSTATS:
        print("Running geomstats benchmarks...")
        try:
            gs_bench = GeomstatsBenchmarks(k, n)
            all_results.extend(gs_bench.run_all(n_trials))
        except Exception as e:
            print(f"  Error: {e}")

    # pymanopt benchmarks
    if HAS_PYMANOPT:
        print("Running pymanopt benchmarks...")
        try:
            pm_bench = PymanoptBenchmarks(k, n)
            all_results.extend(pm_bench.run_all(n_trials))
        except Exception as e:
            print(f"  Error: {e}")

    print()

    # Print results table
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"{'Library':12s} | {'Operation':25s} | {'Mean ± Std':25s}")
    print("-" * 70)

    # Group by operation
    operations = ['random_sample', 'geodesic_distance', 'exp_map', 'log_map', 'parallel_transport']
    for op in operations:
        op_results = [r for r in all_results if r.name == op]
        for r in op_results:
            print(r)
        if len(op_results) > 0:
            print("-" * 70)

    # Summary comparison
    if HAS_GEOMSTATS or HAS_PYMANOPT:
        print()
        print("SPEEDUP vs grasscalc (>1 means grasscalc is faster)")
        print("-" * 50)

        gc_results = {r.name: r for r in all_results if r.library == 'grasscalc'}

        for lib in ['geomstats', 'pymanopt']:
            lib_results = {r.name: r for r in all_results if r.library == lib}
            if lib_results:
                print(f"\n{lib}:")
                for op, gc_r in gc_results.items():
                    if op in lib_results:
                        other_r = lib_results[op]
                        speedup = other_r.mean_time / gc_r.mean_time
                        status = "🚀" if speedup > 1 else "⚠️"
                        print(f"  {op:25s}: {speedup:5.2f}x {status}")

    return all_results


def main():
    """Main entry point."""
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Grassmannian benchmark suite')
    parser.add_argument('-k', type=int, default=5, help='Fiber dimension')
    parser.add_argument('-n', type=int, default=20, help='Ambient dimension')
    parser.add_argument('--trials', type=int, default=100, help='Number of trials')
    args = parser.parse_args()

    run_comparison(args.k, args.n, args.trials)


if __name__ == '__main__':
    main()
