"""
API package — exposes all route modules for easy import in main.py.
"""

from . import routes_auth

__all__ = [
    "routes_auth",
]