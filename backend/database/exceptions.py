from __future__ import annotations


class DatabaseError(Exception):
    """Base exception for database errors."""


class RecordNotFoundError(DatabaseError):
    """Requested record does not exist."""


class DuplicateRecordError(DatabaseError):
    """Unique constraint violation."""


class ConstraintViolationError(DatabaseError):
    """Foreign key or check constraint violation."""


class MigrationError(DatabaseError):
    """Database migration failure."""
