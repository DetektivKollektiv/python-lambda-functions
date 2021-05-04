from core_layer.connection_handler import get_db_session

from core_layer.model.item_model import Item
from ml_service import EnrichItem, get_online_factcheck, GetEntities, GetTags
from core_layer.handler import item_handler, external_factcheck_handler, url_handler, claimant_handler, tag_handler
import json
import time
import pytest
import os


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
            "KeyPhrases": [
                "das Zahlenmaterial",
                "es",
                "den letzten 7 Tagen",
                "das RKI",
                "sich"
            ],
            "Entities": [
                "0,01 Prozent",
                "RKI",
                "Covid",
                "19",
                "Corona Transition"
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
        response = get_online_factcheck.get_online_factcheck(event, context, True, session)
        elapsed = time.perf_counter() - s
        body = response['body']
        # Deserialize if body is string
        if isinstance(body, str):
            factcheck = json.loads(body)
        else:
            factcheck = body
        assert factcheck['url'] == 'https://correctiv.org/faktencheck/2020/07/09/nein-rki-bestaetigt-nicht-eine-covid-19-sterblichkeitsrate-von-001-prozent-in-deutschland/'
        assert factcheck['title'] == 'Falsch. Das Robert-Koch-Institut bestätigte nicht eine Covid-19- Sterblichkeitsrate von 0,01 Prozent in Deutschland.'
        assert elapsed < 3

    def test_get_online_factcheck_by_itemid_2(self, monkeypatch):
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
            "KeyPhrases": [
                "das Zahlenmaterial",
                "es",
                "den letzten 7 Tagen",
                "das RKI",
                "sich"
            ],
            "Entities": [
                "RKI",
                "0,01 Prozent",
                "19 Sterblichkeitsrate",
                "Corona Transition",
                "Covid"
            ],
            "Sentiment": "NEUTRAL"
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
        response = get_online_factcheck.get_online_factcheck(event, context, True, session)
        elapsed = time.perf_counter() - s
        body = response['body']
        # Deserialize if body is string
        if isinstance(body, str):
            factcheck = json.loads(body)
        else:
            factcheck = body
        assert factcheck['url'] == 'https://correctiv.org/faktencheck/2020/07/09/nein-rki-bestaetigt-nicht-eine-covid-19-sterblichkeitsrate-von-001-prozent-in-deutschland/'
        assert factcheck['title'] == 'Falsch. Das Robert-Koch-Institut bestätigte nicht eine Covid-19- Sterblichkeitsrate von 0,01 Prozent in Deutschland.'
        assert elapsed < 3

    def test_get_online_factcheck_by_itemid_3(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        os.environ["STAGE"] = "dev"

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4"
        item.language = "de"
        item = item_handler.create_item(item, True, session)

        # store a fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": item.language,
            },
            "KeyPhrases": [],
            "Entities": [],
            "Sentiment": "NEUTRAL"
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
        response = get_online_factcheck.get_online_factcheck(event, context, True, session)
        elapsed = time.perf_counter() - s
        body = response['body']
        # Deserialize if body is string
        assert body == 'No factcheck found.'
        assert elapsed < 3

    def test_get_online_factcheck_by_itemid_4(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        os.environ["STAGE"] = "dev"

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4"
        item.language = None
        item = item_handler.create_item(item, True, session)

        # store a fact check
        event = {
            "item": {
                "id": item.id,
                "content": item.content,
                "language": item.language,
            },
            "KeyPhrases": [],
            "Entities": [],
            "Sentiment": "NEUTRAL"
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
        response = get_online_factcheck.get_online_factcheck(event, context, True, session)
        elapsed = time.perf_counter() - s
        body = response['body']
        # Deserialize if body is string
        assert body == 'No factcheck found. Exception: Language of Claim not recognized.'
        assert elapsed < 3

    def test_get_online_factcheck_by_itemid_5(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        os.environ["STAGE"] = "dev"

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "Ein in sozialen Medien kursierendes Video soll angeblich große Schwächen der zum Corona-Test genutzten PCR-Methode offenbaren. 'Sensation! Naomi Seibt widerlegt den PCR Test von Prof Drosten! KEIN Virus EXISTENT!!!', heißt es etwa (hier archiviert, hier Video archiviert)"
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
                "Drosten",
                "Test",
                "Corona",
                "PCR"
            ],
            "Entities": []
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
        response = get_online_factcheck.get_online_factcheck(event, context, True, session)
        elapsed = time.perf_counter() - s
        body = response['body']
        # Deserialize if body is string
        if isinstance(body, str):
            factcheck = json.loads(body)
        else:
            factcheck = body
        assert factcheck['url'] == 'https://correctiv.org/faktencheck/2020/11/23/nein-christian-drosten-hat-2014-nicht-gesagt-dass-er-pcr-tests-fuer-untauglich-halte/'
        assert factcheck['title'] == 'Fehlender Kontext. Drosten sagte nicht, PCR-Tests seien „untauglich“ – er kritisierte die Teststrategie 2014 in der MERS-Epidemie. Seine Aussagen lassen sich nicht auf die heutige Coronavirus-Pandemie übertragen.'
        assert elapsed < 3

    def test_get_online_factcheck_by_itemid_6(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        os.environ["STAGE"] = "dev"

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "https://www.pressenza.com/de/2021/01/geoengineering-fuer-bill-gates-ist-die-sonne-das-problem/"
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
                "problem", 
                "gates", 
                "bill"
            ],
            "Entities": [
                "Bill Gates", 
                "Sonne"
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
        response = get_online_factcheck.get_online_factcheck(event, context, True, session)
        elapsed = time.perf_counter() - s
        body = response['body']
        # Deserialize if body is string
        if isinstance(body, str):
            factcheck = json.loads(body)
        else:
            factcheck = body
        assert factcheck['url'] == 'https://correctiv.org/faktencheck/2020/11/23/nein-christian-drosten-hat-2014-nicht-gesagt-dass-er-pcr-tests-fuer-untauglich-halte/'
        assert factcheck['title'] == 'Fehlender Kontext. Drosten sagte nicht, PCR-Tests seien „untauglich“ – er kritisierte die Teststrategie 2014 in der MERS-Epidemie. Seine Aussagen lassen sich nicht auf die heutige Coronavirus-Pandemie übertragen.'
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


class TestStoreTags:
    def test_store_itemtag(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        os.environ["STAGE"] = "dev"

        session = get_db_session(True, None)

        # creating items
        item = Item()
        item.content = "RKI bestätigt Covid-19 Sterblichkeitsrate von 0,01 Prozent in (...) - Corona Transition "
        item.language = "de"
        item = item_handler.create_item(item, True, session)
        list_tags = ['RKI', 'Covid', 'Corona Transition']

        # store tags
        event = {
            "item": item.to_dict(),
            "Tags": list_tags
        }
        context = ""
        EnrichItem.store_itemtags(event, context, True, session)

        tag = tag_handler.get_tag_by_content(list_tags[0], True, session)
        assert tag.tag == list_tags[0]

        itemtag = tag_handler.get_itemtag_by_tag_and_item_id(
            tag.id, item.id, True, session)
        assert itemtag.id is not None

        event = {
            "pathParameters": {
                "item_id": item.id
            }
        }
        ret = GetTags.get_tags_for_item(event, context, True, session)
        body = ret['body']
        # Deserialize if body is string
        if isinstance(body, str):
            tags = json.loads(body)['Tags']
        else:
            tags = body['Tags']
        assert tags == list_tags

# Delete class TestPostTags and replace by test_post_tags_for_item.py ???

# class TestPostTags:
#     def test_post_tags_for_item_1(self, monkeypatch):
#         monkeypatch.setenv("DBNAME", "Test")
#         os.environ["STAGE"] = "dev"

#         session = get_db_session(True, None)

#         # creating items
#         item = Item()
#         item.content = "https://corona-transition.org/rki-bestatigt-covid-19-sterblichkeitsrate-von-0-01-prozent-in" \
#                        "-deutschland?fbclid=IwAR2vLIkW_3EejFaeC5_wC_410uKhN_WMpWDMAcI-dF9TTsZ43MwaHeSl4n8%22 "
#         item.language = "de"
#         item = item_handler.create_item(item, True, session)

#         # store a fact check
#         event = {
#             "item": {
#                 "id": item.id,
#                 "content": item.content,
#                 "language": item.language,
#             },
#             "Tags": [
#                 "RKI",
#                 "Covid",
#                 "Corona Transition"
#             ]
#         }
#         context = ""
#         EnrichItem.store_itemtags(event, context, True, session)

#         event = {
#             "pathParameters": {
#                 "item_id": item.id
#             }
#         }
#         response = GetTags.get_tags_for_item(event, context, True, session)
#         body = response['body']
#         # Deserialize if body is string
#         if isinstance(body, str):
#             tags = json.loads(body)['Tags']
#         else:
#             tags = body['Tags']
#         assert tags == ['RKI', 'Covid', 'Corona Transition']

#         event = {
#             "pathParameters": {
#                 "item_id": item.id
#             },
#             "body": json.dumps({"tags": ['RKI', 'Covid-19']})
#         }
#         response = GetTags.post_tags_for_item(event, context, True, session)
#         body = response['body']
#         # Deserialize if body is string
#         if isinstance(body, str):
#             tags_added = json.loads(body)['added tags']
#             tags_removed = json.loads(body)['removed tags']
#         else:
#             tags_added = body['added tags']
#             tags_removed = body['removed tags']
#         assert tags_added == ['Covid-19']
#         assert len(tags_removed) == 2
#         assert 'Covid' in tags_removed
#         assert 'Corona Transition' in tags_removed
#         response = GetTags.get_tags_for_item(event, context, True, session)
#         body = response['body']
#         # Deserialize if body is string
#         if isinstance(body, str):
#             tags = json.loads(body)['Tags']
#         else:
#             tags = body['Tags']
#         assert tags == ['RKI', 'Covid-19']

#     def test_post_tags_for_item_2(self, monkeypatch):
#         monkeypatch.setenv("DBNAME", "Test")
#         os.environ["STAGE"] = "dev"

#         session = get_db_session(True, None)

#         # creating items
#         item = Item()
#         item.content = "https://corona-transition.org/rki-bestatigt-covid-19-sterblichkeitsrate-von-0-01-prozent-in" \
#                        "-deutschland?fbclid=IwAR2vLIkW_3EejFaeC5_wC_410uKhN_WMpWDMAcI-dF9TTsZ43MwaHeSl4n8%22 "
#         item.language = "de"
#         item = item_handler.create_item(item, True, session)

#         event = {
#             "pathParameters": {
#                 "item_id": item.id
#             }
#         }
#         context = ""
#         response = GetTags.get_tags_for_item(event, context, True, session)
#         body = response['body']
#         # Deserialize if body is string
#         if isinstance(body, str):
#             tags = json.loads(body)['Tags']
#         else:
#             tags = body['Tags']
#         assert tags == []

#         json.dumps({"tags": ["RKI", "Covid-19"]})
#         event = {
#             "pathParameters": {
#                 "item_id": item.id
#             },
#             "body": json.dumps({"tags": ["RKI", "Covid-19"]})
#         }
#         response = GetTags.post_tags_for_item(event, context, True, session)
#         body = response['body']
#         # Deserialize if body is string
#         if isinstance(body, str):
#             tags_added = json.loads(body)['added tags']
#             tags_removed = json.loads(body)['removed tags']
#         else:
#             tags_added = body['added tags']
#             tags_removed = body['removed tags']
#         assert 'RKI' in tags_added
#         assert 'Covid-19' in tags_added
#         assert len(tags_removed) == 0
#         assert tags_removed == []
#         response = GetTags.get_tags_for_item(event, context, True, session)
#         body = response['body']
#         # Deserialize if body is string
#         if isinstance(body, str):
#             tags = json.loads(body)['Tags']
#         else:
#             tags = body['Tags']
#         assert tags == ['RKI', 'Covid-19']