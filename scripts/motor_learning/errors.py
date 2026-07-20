class MotorLearningError(Exception):
    """Base error; fail closed."""


class SchemaError(MotorLearningError):
    pass


class IdempotencyHit(MotorLearningError):
    """Duplicate event already processed; not a hard failure when handled."""


class IllegalTransition(MotorLearningError):
    pass


class GovernanceBlock(MotorLearningError):
    """Ratify/reject/rollback blocked by missing receipt, shadow, or ECQR."""
