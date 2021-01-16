from core_layer.connection_handler import get_db_session

from core_layer.model.item_model import Item
from ml_service import EnrichItem, GetTags
from core_layer.handler import item_handler, tag_handler
import json
import pytest
import os


class test_post_tags_for_item:
    def test_post_tags_for_item_1(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        os.environ["STAGE"] = "dev"

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "https://corona-transition.org/rki-bestatigt-covid-19-sterblichkeitsrate-von-0-01-prozent-in" \
                       "-deutschland?fbclid=IwAR2vLIkW_3EejFaeC5_wC_410uKhN_WMpWDMAcI-dF9TTsZ43MwaHeSl4n8%22 "
        item.language = "de"
        item = item_handler.create_item(item, True, session)

        # store a fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": item.language,
            },
            "Tags": [
                "RKI",
                "Covid",
                "Corona Transition"
            ]
        }
        context = ""
        EnrichItem.store_itemtags(event, context, True, session)

        event = {
            "pathParameters": {
                "item_id": item.id
            }
        }
        context = {}
        response = GetTags.get_tags_for_item(event, context, True, session)
        body = response['body']
        # Deserialize if body is string
        if isinstance(body, str):
            tags = json.loads(body)
        else:
            tags = body
        assert tags == ['RKI']