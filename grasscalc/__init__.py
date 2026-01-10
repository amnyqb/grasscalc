"""
Grassmannian Calculus (grasscalc) - A Python package for calculus on Grassmannian manifolds.

This package implements:
- Layer 1: Within-manifold calculus (differentiation, integration, flows)
- Layer 2: Between-manifold transition calculus (correspondences, sharp bound)
- GCT: Grassmannian Cosmological Theory applications

Reference: Al Yaquob, A. (2026). Grassmannian Calculus and Transition Operators.
"""

__version__ = "0.1.0"
__author__ = "A. Y. Al Yaquob"
__email__ = "amin@alyaquob.com"

# Lazy imports to avoid circular dependencies - imports happen when accessed
def __getattr__(name):
    """Lazy loading of submodules."""
    submodules = ('core', 'layer1', 'layer2', 'gct', 'visualization', 'viz',
                  'validation', 'backends')
    if name in submodules:
        import importlib
        # 'viz' is an alias for 'visualization'
        if name == 'viz':
            name = 'visualization'
        return importlib.import_module(f'.{name}', __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
