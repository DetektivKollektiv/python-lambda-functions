import crud.operations as operations
from crud.model import Item
import json
import pytest


class TestGetFactChecks:
    def test_get_factchecks_by_itemid_db(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        import EnrichItem

        session = operations.get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "item is referencing some fact checks"
        item = operations.create_item_db(item, True, session)

        factcheck = operations.get_factcheck_by_itemid_db(item.id, True, session)
        assert factcheck is None

        # store a fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": "en",
            },
            "FactChecks": [
                {
                    "claimReview": [
                        {
                            "publisher": {
                                "site": "dpa-factchecking.com"
                            },
                            "url": "https://dpa-factchecking.com/austria/200625-99-562594/",
                            "title": "Fotos zeigen Polizisten in Australien - kein Zusammenhang zu Stuttgart",
                            "reviewDate": "2020-06-29T00:00:00Z",
                            "textualRating": "Die Bilder stammen nicht aus Deutschland.",
                            "languageCode": "de"
                        }
                    ]
                }
            ]
        }
        context = ""
        EnrichItem.store_factchecks(event, context, True, session)
        factcheck = operations.get_factcheck_by_itemid_db(item.id, True, session)
        assert factcheck.url == "https://dpa-factchecking.com/austria/200625-99-562594/"

        # store another fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": "en",
            },
            "FactChecks": [
                {
                    "claimReview": [
                        {
                            "publisher": {
                                "site": "leadstories.com"
                            },
                            "url": "https://leadstories.com/hoax-alert/2020/08/fact-check-video-does-not-prove-masks"
                                   "-kill-or-that-microchips-will-be-forced-into-everyone-through-vaccines.html",
                            "title": "Fact Check: Video Does NOT Prove Face Masks Kill",
                            "reviewDate": "2020-08-07T19:16:06Z",
                            "textualRating": "Bad Info",
                            "languageCode": "en"
                        }
                    ]
                }
            ]
        }
        context = ""
        EnrichItem.store_factchecks(event, context, True, session)
        factcheck = operations.get_factcheck_by_itemid_db(item.id, True, session)
        assert factcheck.url == "https://dpa-factchecking.com/austria/200625-99-562594/"

    def test_get_factcheck_by_itemid(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        import app
        import EnrichItem

        session = operations.get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "item is referencing some fact checks"
        item = operations.create_item_db(item, True, session)

        # store a fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": "en",
            },
            "FactChecks": [
                {
                    "claimReview": [
                        {
                            "publisher": {
                                "site": "dpa-factchecking.com"
                            },
                            "url": "https://dpa-factchecking.com/austria/200625-99-562594/",
                            "title": "Fotos zeigen Polizisten in Australien - kein Zusammenhang zu Stuttgart",
                            "reviewDate": "2020-06-29T00:00:00Z",
                            "textualRating": "Die Bilder stammen nicht aus Deutschland.",
                            "languageCode": "de"
                        }
                    ]
                }
            ]
        }
        context = ""
        EnrichItem.store_factchecks(event, context, True, session)

        # store another fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": "en",
            },
            "FactChecks": [
                {
                    "claimReview": [
                        {
                            "publisher": {
                                "site": "leadstories.com"
                            },
                            "url": "https://leadstories.com/hoax-alert/2020/08/fact-check-video-does-not-prove-masks"
                                   "-kill-or-that-microchips-will-be-forced-into-everyone-through-vaccines.html",
                            "title": "Fact Check: Video Does NOT Prove Face Masks Kill",
                            "reviewDate": "2020-08-07T19:16:06Z",
                            "textualRating": "Bad Info",
                            "languageCode": "en"
                        }
                    ]
                }
            ]
        }
        context = ""
        EnrichItem.store_factchecks(event, context, True, session)

        event = {
            "pathParameters": {
                "item_id": item.id
            }
        }
        context = {}
        response = app.get_factcheck_by_itemid(event, context, True, session)
        body = response['body']
        # Deserialize if body is string
        if isinstance(body, str):
            factcheck = json.loads(body)
        else:
            factcheck = body
        assert factcheck['url'] == "https://dpa-factchecking.com/austria/200625-99-562594/"
        assert factcheck['title'] == "Fotos zeigen Polizisten in Australien - kein Zusammenhang zu Stuttgart"

    def test_store_factcheck_empty(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        import EnrichItem

        session = operations.get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "item is referencing some fact checks"
        item = operations.create_item_db(item, True, session)

        # store a fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": "en",
            },
            "FactChecks": [
                ""
            ]
        }
        context = ""
        ret = EnrichItem.store_factchecks(event, context, True, session)
        assert ret is None

    def test_store_itemurl(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        import EnrichItem
        from urllib.parse import urlparse

        session = operations.get_db_session(True, None)

        str_url = "https://smopo.ch/zehntausende-als-falsche-coronatote-deklariert/"
        # creating items
        item = Item()
        item.content = str_url
        item = operations.create_item_db(item, True, session)

        # store a url
        event = {
            "item": item.to_dict(),
            "Claim": {
                "urls": [
                    str_url
                ]
            }
        }
        context = ""
        EnrichItem.store_itemurl(event, context, True, session)

        url = operations.get_url_by_content_db(str_url, True, session)
        itemurl = operations.get_itemurl_by_url_and_item_db(url.id, item.id, True, session)
        domain = urlparse(str_url).hostname
        claimant = operations.get_claimant_by_name_db(domain, True, session)

        assert url.url == str_url
        assert itemurl.id is not None
        assert claimant.claimant == domain
