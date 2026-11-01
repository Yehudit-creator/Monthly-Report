
from abc import ABC, abstractmethod

from models.report import Report


class BaseRenderer(ABC):
    """Base class for report renderers."""

    @abstractmethod
    def render(
        self,
        report: Report,
        output_path: str
    ) -> None:
        """Generate a file from the report."""
        pass
