import csv
import io

from yandex_py.constants import MISSING_VALUE
from yandex_py.direct.reports.types.fields import FieldName

ReportRow = dict[FieldName, str | None]


def parse_report(tsv: str) -> list[ReportRow]:
    """
    Парсит TSV-ответ API Яндекс.Директ в список словарей.

    Ожидает ответ с skipReportHeader=true и skipReportSummary=true.
    Значение '--' (отсутствующие данные) преобразуется в None.
    """
    reader = csv.DictReader(io.StringIO(tsv.strip()), delimiter="\t")

    if reader.fieldnames is None:
        return []

    unknown = [f for f in reader.fieldnames if f not in FieldName._value2member_map_]
    if unknown:
        raise ValueError(f"Неизвестные поля в ответе: {unknown}")

    rows: list[ReportRow] = []
    for raw_row in reader:
        row: ReportRow = {
            FieldName(key): (None if value == MISSING_VALUE else value)
            for key, value in raw_row.items()
            if key is not None
        }
        rows.append(row)

    return rows
