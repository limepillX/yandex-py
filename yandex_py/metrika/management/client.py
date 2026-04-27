from __future__ import annotations

from yandex_py.core.transport import HTTPTransport
from yandex_py.metrika.constants import MANAGEMENT_COUNTERS_PATH
from yandex_py.metrika.errors import raise_metrika_api_error
from yandex_py.metrika.management.types import CounterGoal, CounterGoalsResponse


class MetrikaManagementAPI:
    def __init__(self, transport: HTTPTransport):
        self._transport = transport

    def get_goals_by_counter_sync(self, counter_id: int) -> list[CounterGoal]:
        response = self._transport.get(
            MANAGEMENT_COUNTERS_PATH,
            params={
                "counter_ids": str(counter_id),
                "field": "goals",
            },
            headers={"Accept": "application/json"},
        )
        return self._parse_goals_response(response, counter_id)

    async def get_goals_by_counter(self, counter_id: int) -> list[CounterGoal]:
        response = await self._transport.get_async(
            MANAGEMENT_COUNTERS_PATH,
            params={
                "counter_ids": str(counter_id),
                "field": "goals",
            },
            headers={"Accept": "application/json"},
        )
        return self._parse_goals_response(response, counter_id)

    def _parse_goals_response(self, response, counter_id: int) -> list[CounterGoal]:
        if response.status_code != 200:
            raise_metrika_api_error(response)

        payload = CounterGoalsResponse.model_validate(response.json())
        for counter in payload.counters:
            if counter.id == counter_id:
                return counter.goals
        return []
