from models.report_type import ReportType
from parsing.BaseParser import ReportParser
from parsing.TypeAParser import ReportParserA
from parsing.TypeBParser import ReportParserB

_PARSERS: dict[ReportType, type[ReportParser]] = {
    ReportType.A: ReportParserA,
    ReportType.B: ReportParserB,
}


def get_parser(report_type: ReportType) -> ReportParser:
    if report_type not in _PARSERS:
        raise ValueError(f"Unknown report type: {report_type}")
    return _PARSERS[report_type]()