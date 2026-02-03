"""Exceptions used by deployments of the pipeline components"""


class CancellationException(Exception):
    """Exception raised when a job is cancelled"""
    pass
