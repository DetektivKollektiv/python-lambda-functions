import logging
import json

from typing import Any
from .boto_client_provider import BotoClientProvider


class EventPublisher:

    _client: Any
    _logger: logging.Logger

    def __init__(self) -> None:
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)

        self._client = BotoClientProvider().get_client('events')
        pass

    def publish_event(self, source: str, detail_type: str, details: dict) -> None:

        if not source:
            raise Exception

        if not detail_type:
            raise Exception

        try:

            entries = [{
                'Source': source,
                'DetailType': detail_type,
                'Detail': json.dumps(details),
                'Resources': []
            }]

            result = self._client.put_events(Entries=entries)

            if('FailedEntryCount' in result and result['FailedEntryCount'] > 0):
                self._logger.error(
                    f"Failed to publish {result['FailedEntryCount']} events.")
            pass
        except Exception as ex:
            self._logger.error(ex)
            raise ex
        pass
