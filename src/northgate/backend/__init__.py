"""Northgate backend: read-only data access, analytics and model-inference status.

The dashboard (or a future HTTP API) should import only from `northgate.backend.api`.
Nothing in this package trains a model, downloads data or writes to the dataset.
"""
