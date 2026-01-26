"""Package marker for `service` package.

Avoid importing submodules at package import time to prevent import-time
side-effects (and hard dependency requirements) when tests import
`service.some_module`. Individual service modules should be imported
explicitly by consumers.
"""

__all__ = []