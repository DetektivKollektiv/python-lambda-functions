from core_layer.db_handler import Session
from core_layer.model.item_model import Item
from core_layer.model.tag_model import Tag
from ml_service import EnrichItem, GetTags
from core_layer.handler import item_handler
import json
import os


def test_post_tags_for_item():
    # pre-stuff
    os.environ["STAGE"] = "dev"

    with Session() as session:

        # create item
        item = Item()
        item.content = "https://corona-transition.org/rki-bestatigt-covid-19-sterblichkeitsrate-von-0-01-prozent-in" \
                        "-deutschland?fbclid=IwAR2vLIkW_3EejFaeC5_wC_410uKhN_WMpWDMAcI-dF9TTsZ43MwaHeSl4n8%22 "
        item.language = "de"
        item = item_handler.create_item(item, session)

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
        EnrichItem.store_itemtags(event, context)

        # create event
        event = {
            "pathParameters": {
                "item_id": item.id
            }
        }

        response = GetTags.get_tags_for_item(event, context)
        body = response['body']
        tags = json.loads(body)['Tags']
        assert tags == ['RKI', 'Covid', 'Corona Transition']

        # create event with 1 already existing tag and 1 new tag
        event = {
            "pathParameters": {
                "item_id": item.id
            },
            "body": json.dumps({"tags": ['RKI', 'Covid-19']})
        }

        response = GetTags.post_tags_for_item(event, context)
        body = response['body']
        tags_added = json.loads(body)['added new tags']
        tags_counter_increased = json.loads(body)['increased tag counter']
        assert tags_added == ['Covid-19']
        assert len(tags_counter_increased) == 1
        assert 'RKI' in tags_counter_increased
        assert 'Covid-19' not in tags_counter_increased

        response = GetTags.get_tags_for_item(event, context)
        body = response['body']
        tags = json.loads(body)['Tags']
        assert tags == ['RKI', 'Covid', 'Corona Transition', 'Covid-19']

        # Check counts: RKI posted twice, all other once
        assert session.query(Tag).filter_by(tag = 'RKI').first().items[0].count == 2
        assert session.query(Tag).filter_by(tag = 'Covid').first().items[0].count == 1
        assert session.query(Tag).filter_by(tag = 'Corona Transition').first().items[0].count == 1
        assert session.query(Tag).filter_by(tag = 'Covid-19').first().items[0].count == 1
