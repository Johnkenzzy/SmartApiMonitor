"""
API package — exposes all route modules for easy import in main.py.
"""

from . import routes_auth, routes_celery

__all__ = [
    "routes_auth",
]