from core_layer.connection_handler import get_db_session

from core_layer.model.item_model import Item
from ml_service import EnrichItem, get_online_factcheck
from core_layer.handler import item_handler, external_factcheck_handler, url_handler, claimant_handler
import json
import time
import pytest


class TestGetFactChecks:
    def test_get_factchecks_by_itemid_db(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        # import EnrichItem

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "item is referencing some fact checks"
        item = item_handler.create_item(item, True, session)

        factcheck = external_factcheck_handler.get_factcheck_by_itemid(
            item.id, True, session)
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
        factcheck = external_factcheck_handler.get_factcheck_by_itemid(
            item.id, True, session)
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
        factcheck = external_factcheck_handler.get_factcheck_by_itemid(
            item.id, True, session)
        assert factcheck.url == "https://dpa-factchecking.com/austria/200625-99-562594/"

    def test_get_online_factcheck_by_itemid(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")

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
            "KeyPhrases": [
                "das Zahlenmaterial",
                "es",
                "den letzten 7 Tagen",
                "das RKI",
                "sich"
            ],
            "Entities": [
                "26. Juni 2020",
                "Deutschland",
                "0,01 Prozent",
                "83 Millionen Einwohnern",
                "136 Kreisen",
                "RKI",
                "0,01 Prozent",
                "Covid",
                "19",
                "Corona Transition"
            ],
            "TitleEntities": [
            ]
        }
        context = ""
        EnrichItem.store_itementities(event, context, True, session)
        EnrichItem.store_itemphrases(event, context, True, session)

        event = {
            "pathParameters": {
                "item_id": item.id
            }
        }
        context = {}
        s = time.perf_counter()
        response = get_online_factcheck.get_online_factcheck(
            event, context, True, session)
        elapsed = time.perf_counter() - s
        body = response['body']
        # Deserialize if body is string
        if isinstance(body, str):
            factcheck = json.loads(body)
        else:
            factcheck = body
        assert factcheck['url'] == 'https://dpa-factchecking.com/germany/200924-99-688034'

        assert factcheck['title'] == 'Gericht erklärte Wahlgesetz, nicht aber alle Wahlen seit 1956 für nichtig'
        assert elapsed < 3


class TestStoreFactChecks:
    def test_store_factcheck_empty(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "item is referencing some fact checks"
        item = item_handler.create_item(item, True, session)

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
        EnrichItem.store_factchecks(event, context, True, session)
        assert 1 == 1


class TestStoreURLs:
    def test_store_itemurl(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        from urllib.parse import urlparse

        session = get_db_session(True, None)

        str_url = "https://smopo.ch/zehntausende-als-falsche-coronatote-deklariert/"
        # creating items
        item = Item()
        item.content = str_url
        item = item_handler.create_item(item, True, session)

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

        url = url_handler.get_url_by_content(str_url, True, session)
        itemurl = url_handler.get_itemurl_by_url_and_item_id(
            url.id, item.id, True, session)
        domain = urlparse(str_url).hostname
        claimant = claimant_handler.get_claimant_by_name(domain, True, session)

        assert url.url == str_url
        assert itemurl.id is not None
        assert claimant.claimant == domain
        assert url.claimant_id is not None
