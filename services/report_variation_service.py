from models.report import Report
from services.transformations.base_transformation_strategy import (
    BaseTransformationStrategy,
)


class ReportVariationService:
    """Service for creating report variations."""

    def __init__(
        self,
        strategy: BaseTransformationStrategy
    ):
        self.strategy = strategy

    def create_variation(
        self,
        report: Report,
        offset_minutes: int
    ) -> Report:
        return self.strategy.transform(
            report,
            offset_minutes
        )