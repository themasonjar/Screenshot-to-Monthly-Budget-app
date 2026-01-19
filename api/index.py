"""
Vercel Serverless Function entrypoint.

Vercel's Python runtime will detect the exported `app` WSGI application.
"""

from backend.app import app  # noqa: F401

