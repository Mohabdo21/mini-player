"""
Development init file to facilitate importing from the src directory.

This file ensures that when running from the development directory
structure, the miniplayer package can be properly imported.
"""

# Add an import that forces relative imports to work correctly
from . import miniplayer
