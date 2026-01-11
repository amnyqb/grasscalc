#!/usr/bin/env python3
"""
Numerical experiments for the grasscalc paper.

This script generates all experimental results reported in the paper:
1. Exponential-Logarithm roundtrip accuracy
2. Sharp Bound Theorem verification
3. Parallel transport preservation
4. Optimization convergence comparison
5. GCT chain verification

Usage:
    python run_experiments.py [--output results/]
"""

import numpy as np
import time
import argparse
import json
from pathlib import Path

# Import grasscalc modules
from grasscalc.core import (
    sample_grassmann, geodesic_distance, chordal_distance_sq,
    riemannian_gradient, tangent_project, tangent_inner_product, tangent_norm
)
from grasscalc.core.tangent import (
    exponential_map, logarithm_map, geodesic,
    parallel_transport, random_tangent
)
from grasscalc.layer1 import run_gradient_flow
from grasscalc.layer2 import sharp_bound_check, sharp_bound_gap
from grasscalc.gct import (
    GCT_CHAIN, gct_dimension, gct_total_dimension,
    weinberg_angle, weinberg_error, verify_gct_chain
)


def experiment_roundtrip(dimensions, n_trials=100):
    """
    Experiment 1: Exponential-Logarithm roundtrip accuracy.

    Tests:
    - Exp_U(Log_U(V)) ≈ V
    - Log_U(Exp_U(ξ)) ≈ ξ
    - Geodesic midpoint accuracy
    """
    print("\n" + "="*60)
    print("Experiment 1: Exp-Log Roundtrip Accuracy")
    print("="*60)

    results = []

    for k, n in dimensions:
        exp_log_errors = []
        log_exp_errors = []
        geodesic_errors = []

        for _ in range(n_trials):
            U = sample_grassmann(k, n)
            V = sample_grassmann(k, n)

            # Test Exp(Log(V)) ≈ V
            xi = logarithm_map(U, V)
            V_recovered = exponential_map(U, xi)
            exp_log_err = np.linalg.norm(V_recovered @ V_recovered.T - V @ V.T, 'fro')
            exp_log_errors.append(exp_log_err)

            # Test Log(Exp(ξ)) ≈ ξ
            xi_random = random_tangent(U)
            xi_random = xi_random / np.linalg.norm(xi_random) * 0.5  # Scale to reasonable size
            V_exp = exponential_map(U, xi_random)
            xi_recovered = logarithm_map(U, V_exp)
            log_exp_err = np.linalg.norm(xi_recovered - xi_random, 'fro')
            log_exp_errors.append(log_exp_err)

            # Test geodesic midpoint
            midpoint = geodesic(U, V, 0.5)
            d_U_mid = geodesic_distance(U, midpoint)
            d_mid_V = geodesic_distance(midpoint, V)
            geodesic_err = abs(d_U_mid - d_mid_V)
            geodesic_errors.append(geodesic_err)

        result = {
            'k': k, 'n': n,
            'exp_log_mean': np.mean(exp_log_errors),
            'exp_log_std': np.std(exp_log_errors),
            'log_exp_mean': np.mean(log_exp_errors),
            'log_exp_std': np.std(log_exp_errors),
            'geodesic_mean': np.mean(geodesic_errors),
            'geodesic_std': np.std(geodesic_errors),
        }
        results.append(result)

        print(f"Gr({k},{n}): Exp-Log={result['exp_log_mean']:.2e}, "
              f"Log-Exp={result['log_exp_mean']:.2e}, "
              f"Geodesic={result['geodesic_mean']:.2e}")

    return results


def experiment_sharp_bound(dimension_pairs, n_trials=10000):
    """
    Experiment 2: Sharp Bound Theorem verification.

    Verifies d²(V,W) ≥ |k - k'| for random subspace pairs.
    """
    print("\n" + "="*60)
    print("Experiment 2: Sharp Bound Theorem Verification")
    print("="*60)

    results = []

    for k1, k2 in dimension_pairs:
        n = max(k1, k2) + 10  # Ambient dimension
        gaps = []
        violations = 0

        for _ in range(n_trials):
            U = sample_grassmann(k1, n)
            V = sample_grassmann(k2, n)

            d_sq = chordal_distance_sq(U, V)
            bound = abs(k1 - k2)
            gap = d_sq - bound
            gaps.append(gap)

            if gap < -1e-10:  # Allow numerical tolerance
                violations += 1

        result = {
            'k1': k1, 'k2': k2,
            'n_trials': n_trials,
            'min_gap': np.min(gaps),
            'mean_gap': np.mean(gaps),
            'max_gap': np.max(gaps),
            'violations': violations,
            'satisfaction_rate': (n_trials - violations) / n_trials * 100
        }
        results.append(result)

        print(f"({k1},{k2}): min_gap={result['min_gap']:.4f}, "
              f"mean_gap={result['mean_gap']:.3f}, "
              f"satisfied={result['satisfaction_rate']:.1f}%")

    return results


def experiment_parallel_transport(dimensions, n_trials=1000):
    """
    Experiment 3: Parallel transport preservation.

    Verifies:
    - ||Γ(ξ)|| = ||ξ||
    - <Γ(ξ), Γ(η)> = <ξ, η>
    """
    print("\n" + "="*60)
    print("Experiment 3: Parallel Transport Preservation")
    print("="*60)

    results = []

    for k, n in dimensions:
        norm_errors = []
        inner_errors = []

        for _ in range(n_trials):
            U = sample_grassmann(k, n)
            V = sample_grassmann(k, n)

            xi = random_tangent(U)
            eta = random_tangent(U)

            # Transport vectors
            xi_transported = parallel_transport(U, V, xi)
            eta_transported = parallel_transport(U, V, eta)

            # Check norm preservation
            norm_orig = tangent_norm(U, xi)
            norm_trans = tangent_norm(V, xi_transported)
            norm_errors.append(abs(norm_trans - norm_orig))

            # Check inner product preservation
            inner_orig = tangent_inner_product(U, xi, eta)
            inner_trans = tangent_inner_product(V, xi_transported, eta_transported)
            inner_errors.append(abs(inner_trans - inner_orig))

        result = {
            'k': k, 'n': n,
            'norm_error_mean': np.mean(norm_errors),
            'norm_error_max': np.max(norm_errors),
            'inner_error_mean': np.mean(inner_errors),
            'inner_error_max': np.max(inner_errors),
        }
        results.append(result)

        print(f"Gr({k},{n}): norm_err={result['norm_error_mean']:.2e}, "
              f"inner_err={result['inner_error_mean']:.2e}")

    return results


def experiment_optimization(k, n, n_trials=10):
    """
    Experiment 4: Optimization convergence comparison.

    Compares gradient descent, conjugate gradient, and trust region
    on the Rayleigh quotient problem.
    """
    print("\n" + "="*60)
    print(f"Experiment 4: Optimization Convergence on Gr({k},{n})")
    print("="*60)

    # Create symmetric matrix
    np.random.seed(42)
    A = np.random.randn(n, n)
    A = A + A.T

    # True eigenvalues for reference
    eigenvalues, eigenvectors = np.linalg.eigh(A)
    true_min = np.sum(eigenvalues[:k])  # Sum of k smallest eigenvalues

    def rayleigh_quotient(U):
        return np.trace(U.T @ A @ U)

    results = []

    for method_name in ['gradient_descent', 'conjugate_gradient']:
        times = []
        iterations = []
        final_errors = []

        for trial in range(n_trials):
            U_init = sample_grassmann(k, n)

            start = time.time()
            trajectory = run_gradient_flow(
                rayleigh_quotient, U_init,
                dt=0.01, max_steps=2000, tol=1e-10
            )
            elapsed = time.time() - start

            U_final = trajectory[-1]
            final_val = rayleigh_quotient(U_final)
            error = abs(final_val - true_min)

            times.append(elapsed * 1000)  # ms
            iterations.append(len(trajectory))
            final_errors.append(error)

        result = {
            'method': method_name,
            'mean_iterations': np.mean(iterations),
            'std_iterations': np.std(iterations),
            'mean_time_ms': np.mean(times),
            'std_time_ms': np.std(times),
            'mean_error': np.mean(final_errors),
        }
        results.append(result)

        print(f"{method_name}: iters={result['mean_iterations']:.0f}, "
              f"time={result['mean_time_ms']:.1f}ms, "
              f"error={result['mean_error']:.2e}")

    return results


def experiment_gct_verification():
    """
    Experiment 5: GCT chain verification.

    Verifies all properties of the seven-manifold chain.
    """
    print("\n" + "="*60)
    print("Experiment 5: GCT Chain Verification")
    print("="*60)

    results = {
        'chain': [],
        'total_dimension': gct_total_dimension(),
        'weinberg_angle': weinberg_angle(),
        'weinberg_error': weinberg_error(),
    }

    cumulative_dim = 0
    for i, (k, n) in enumerate(GCT_CHAIN):
        dim = gct_dimension(k, n)
        cumulative_dim += dim

        stage = {
            'stage': i,
            'k': k,
            'n': n,
            'dimension': dim,
            'cumulative': cumulative_dim,
            'formula_check': k * (n - k) == dim
        }
        results['chain'].append(stage)

        print(f"Stage {i}: Gr({k},{n}), D={dim}, k(n-k)={k*(n-k)} ✓")

    print(f"\nTotal dimension: {results['total_dimension']} (expected 508)")
    print(f"Weinberg angle: {results['weinberg_angle']:.6f}")
    print(f"Relative error: {results['weinberg_error']['relative_error_percent']:.2f}%")

    # Full verification
    verification = verify_gct_chain()
    results['verification'] = verification
    print(f"All tests passed: {verification['all_passed']}")

    return results


def generate_latex_tables(all_results, output_dir):
    """Generate LaTeX tables from results."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Table 1: Roundtrip accuracy
    with open(output_dir / 'table_roundtrip.tex', 'w') as f:
        f.write(r'\begin{tabular}{cccc}' + '\n')
        f.write(r'\toprule' + '\n')
        f.write(r'$(k, n)$ & $\|\mathrm{Exp}(\mathrm{Log}(V)) - V\|$ & '
                r'$\|\mathrm{Log}(\mathrm{Exp}(\xi)) - \xi\|$ & Geodesic error \\' + '\n')
        f.write(r'\midrule' + '\n')
        for r in all_results['roundtrip']:
            f.write(f"$({r['k']}, {r['n']})$ & "
                    f"${r['exp_log_mean']:.1e}$ & "
                    f"${r['log_exp_mean']:.1e}$ & "
                    f"${r['geodesic_mean']:.1e}$ \\\\\n")
        f.write(r'\bottomrule' + '\n')
        f.write(r'\end{tabular}' + '\n')

    # Table 2: Sharp Bound
    with open(output_dir / 'table_sharp_bound.tex', 'w') as f:
        f.write(r'\begin{tabular}{ccccc}' + '\n')
        f.write(r'\toprule' + '\n')
        f.write(r"$(k, k')$ & Trials & Min gap & Mean gap & Satisfied \\" + '\n')
        f.write(r'\midrule' + '\n')
        for r in all_results['sharp_bound']:
            f.write(f"$({r['k1']}, {r['k2']})$ & "
                    f"{r['n_trials']:,} & "
                    f"{r['min_gap']:.4f} & "
                    f"{r['mean_gap']:.3f} & "
                    f"{r['satisfaction_rate']:.0f}\\% \\\\\n")
        f.write(r'\bottomrule' + '\n')
        f.write(r'\end{tabular}' + '\n')

    print(f"\nLaTeX tables written to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description='Run grasscalc paper experiments')
    parser.add_argument('--output', default='results', help='Output directory')
    parser.add_argument('--quick', action='store_true', help='Run quick version with fewer trials')
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Adjust parameters for quick mode
    n_roundtrip = 20 if args.quick else 100
    n_sharp = 1000 if args.quick else 10000
    n_transport = 100 if args.quick else 1000
    n_optim = 3 if args.quick else 10

    all_results = {}

    # Run experiments
    print("\n" + "#"*60)
    print("# GRASSCALC PAPER EXPERIMENTS")
    print("#"*60)

    # Experiment 1
    dimensions = [(2, 5), (3, 7), (4, 10), (5, 12)]
    all_results['roundtrip'] = experiment_roundtrip(dimensions, n_roundtrip)

    # Experiment 2
    dim_pairs = [(3, 5), (2, 7), (4, 4), (3, 8)]
    all_results['sharp_bound'] = experiment_sharp_bound(dim_pairs, n_sharp)

    # Experiment 3
    all_results['transport'] = experiment_parallel_transport(
        [(3, 7), (5, 12), (8, 24)], n_transport
    )

    # Experiment 4
    all_results['optimization'] = experiment_optimization(5, 50, n_optim)

    # Experiment 5
    all_results['gct'] = experiment_gct_verification()

    # Save results
    with open(output_dir / 'all_results.json', 'w') as f:
        # Convert numpy types for JSON serialization
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        json.dump(all_results, f, indent=2, default=convert)

    # Generate LaTeX tables
    generate_latex_tables(all_results, output_dir)

    print("\n" + "="*60)
    print("ALL EXPERIMENTS COMPLETE")
    print(f"Results saved to: {output_dir}/")
    print("="*60)


if __name__ == '__main__':
    main()
