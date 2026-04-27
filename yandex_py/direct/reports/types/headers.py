from enum import Enum

from pydantic import BaseModel, Field


class ProcessingMode(str, Enum):
    """
    Режим обработки отчета.
    - auto — Сервер автоматически выбирает режим формирования отчета. Если отчет успешно сформирован в режиме онлайн,
    он будет передан в теле ответа. Если отчет не может быть сформирован в режиме онлайн,
    он ставится в очередь на формирование в режиме офлайн. Приложение должно поддерживать оба режима.
    Отсутствие заголовка эквивалентно значению auto.


    - offline — Отчет ставится в очередь на формирование в режиме офлайн. Проверять готовность отчета нужно
    с помощью повторных запросов с теми же параметрами, см. подраздел Как проверить готовность офлайн-отчета.
    Рекомендуемый интервал проверки указан в HTTP-заголовке ответа retryIn. Если формирование отчета завершено успешно,
    сервер возвращает отчет в теле ответа.

    - online — Отчет формируется в режиме онлайн. Если отчет успешно сформирован, он будет передан в
    теле ответа. Если отчет не может быть сформирован в режиме онлайн, возвращается ошибка.
    """

    auto = "auto"
    offline = "offline"
    online = "online"


class AcceptLanguage(str, Enum):
    """
    Язык, на котором возвращаются названия полей в отчете. Допустимые значения: ru, en. Если заголовок не указан, названия полей возвращаются на
    русском языке.
    """

    ru = "ru"
    en = "en"


class Headers(BaseModel):
    """
    Заголовки запроса

    В дополнение к заголовкам Authorization, Accept-Language, Client-Login можно указать следующие заголовки:

    authorization
    Заголовок Authorization должен содержать строку вида Bearer <токен>, где <токен> — это токен доступа, полученный в результате аутентификации. Подробнее см. раздел Получение токена доступа.

    accept_language: "en"
    Язык, на котором возвращаются названия полей в отчете. Допустимые значения: ru, en. Если заголовок не указан, названия полей возвращаются на
    русском языке.

    client_login
    Логин рекламодателя — клиента рекламного агентства. Обязателен, если запрос осуществляется от имени агентства.

    processing_mode: "auto"
    Режим формирования отчета: online, offline или auto. Отсутствие заголовка эквивалентно значению auto. Описание режимов приведено в разделе Онлайн- и офлайн-отчет.

    return_money_in_micros
    Если заголовок указан, денежные значения в отчете возвращаются в валюте с точностью до двух знаков после запятой. Если не указан, денежные значения возвращаются в виде целых чисел — сумм в валюте, умноженных на 1 000 000.

    skup_report_header: True
    Не выводить в отчете строку с названием отчета и диапазоном дат.

    skip_column_header: False
    Не выводить в отчете строку с названиями полей.

    skip_report_summary: True
    Не выводить в отчете строку с количеством строк статистики.

    accept_encoding: "gzip"
    Если заголовок указан, применяется сжатие gzip.
    """

    authorization: str = Field(..., alias="Authorization")
    client_login: str = Field(..., alias="Client-Login")
    accept_language: AcceptLanguage = Field(AcceptLanguage.ru, alias="Accept-Language")
    processing_mode: str = Field("auto", alias="processingMode")
    return_money_in_micros: bool = Field(False, alias="returnMoneyInMicros")
    skip_report_header: bool = Field(True, alias="skipReportHeader")
    skip_column_header: bool = Field(False, alias="skipColumnHeader")
    skip_report_summary: bool = Field(True, alias="skipReportSummary")
    accept_encoding: str = Field("gzip", alias="Accept-Encoding")
