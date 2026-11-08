
from abc import ABC, abstractmethod
from pathlib import Path

from models.report import Report


class BaseRenderer(ABC):
    """Base class for report renderers."""
    file_extension: str
    @abstractmethod
    def render(
        self,
        report: Report
    ) -> None:
        """Generate a file from the report."""
        pass
