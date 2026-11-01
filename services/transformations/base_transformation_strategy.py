
from abc import ABC, abstractmethod
from models.report import Report


class BaseTransformationStrategy(ABC):
    """Base class for report transformation strategies."""

    @abstractmethod
    def transform(
        self,
        report: Report,
        offset_minutes: int,
    ) -> Report:
        """Return a transformed copy of the report."""
        pass
