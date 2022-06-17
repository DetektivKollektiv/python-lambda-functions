import json
import time
import os
from core_layer.db_handler import Session
from core_layer.model.item_model import Item
from core_layer.handler import item_handler, external_factcheck_handler, tag_handler
from ml_service import EnrichItem, get_online_factcheck, GetTags
import pytest

from core_layer.test.helper.fixtures import database_fixture

class TestGetFactChecks:    
    def test_get_factchecks_by_itemid_db(self, database_fixture):

        with Session() as session:

            # creating items
            item = Item()
            item.content = "item is referencing some fact checks"
            item = item_handler.create_item(item, session)

            factcheck = external_factcheck_handler.get_factcheck_by_itemid(item.id, session)
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
            EnrichItem.store_factchecks(event, context)
            factcheck = external_factcheck_handler.get_factcheck_by_itemid(item.id, session)
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
            EnrichItem.store_factchecks(event, context)
            factcheck = external_factcheck_handler.get_factcheck_by_itemid(
                item.id, session)
            assert factcheck.url == "https://dpa-factchecking.com/austria/200625-99-562594/"


    @pytest.mark.skip(reason="Different API response")
    def test_get_online_factcheck_by_itemid(self):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            # creating items
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
            EnrichItem.store_itementities(event, context)
            EnrichItem.store_itemphrases(event, context)

            event = {
                "pathParameters": {
                    "item_id": item.id
                }
            }
            context = {}
            s = time.perf_counter()
            response = get_online_factcheck.get_online_factcheck(event, context)
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

    def test_get_online_factcheck_by_itemid_2(self, database_fixture):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            # creating items
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
            EnrichItem.store_itementities(event, context)
            EnrichItem.store_itemphrases(event, context)

            event = {
                "pathParameters": {
                    "item_id": item.id
                }
            }
            context = {}
            response = get_online_factcheck.get_online_factcheck(event, context)
            
            body = response['body']
            # Deserialize if body is string
            if isinstance(body, str):
                factcheck = json.loads(body)
            else:
                factcheck = body
            assert factcheck['url'] == 'https://correctiv.org/faktencheck/2020/07/09/nein-rki-bestaetigt-nicht-eine-covid-19-sterblichkeitsrate-von-001-prozent-in-deutschland/'
            assert factcheck['title'] == 'Falsch. Das Robert-Koch-Institut bestätigte nicht eine Covid-19- Sterblichkeitsrate von 0,01 Prozent in Deutschland.'
            
    
    def test_get_online_factcheck_by_itemid_3(self, database_fixture):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            # creating items
            item = Item()
            item.content = "https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4"
            item.language = "de"
            item = item_handler.create_item(item, session)

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
            EnrichItem.store_itementities(event, context)
            EnrichItem.store_itemphrases(event, context)

            event = {
                "pathParameters": {
                    "item_id": item.id
                }
            }
            context = {}
            s = time.perf_counter()
            response = get_online_factcheck.get_online_factcheck(event, context)
            elapsed = time.perf_counter() - s
            body = response['body']
            # Deserialize if body is string
            assert body == 'No factcheck found.'
            assert elapsed < 3    

    def test_get_online_factcheck_by_itemid_4(self, database_fixture):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            # creating items
            item = Item()
            item.content = "https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4"
            item.language = None
            item = item_handler.create_item(item, session)

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
            EnrichItem.store_itementities(event, context)
            EnrichItem.store_itemphrases(event, context)

            event = {
                "pathParameters": {
                    "item_id": item.id
                }
            }
            context = {}
            s = time.perf_counter()
            response = get_online_factcheck.get_online_factcheck(event, context)
            elapsed = time.perf_counter() - s
            body = response['body']
            # Deserialize if body is string
            assert 'Language of Claim not recognized.' in body
            assert elapsed < 3    
    
    @pytest.mark.skip(reason="Different API response")
    def test_get_online_factcheck_by_itemid_5(self):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            # creating items
            item = Item()
            item.content = "Ein in sozialen Medien kursierendes Video soll angeblich große Schwächen der zum Corona-Test genutzten PCR-Methode offenbaren. 'Sensation! Naomi Seibt widerlegt den PCR Test von Prof Drosten! KEIN Virus EXISTENT!!!', heißt es etwa (hier archiviert, hier Video archiviert)"
            item.language = "de"
            item = item_handler.create_item(item, session)

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
            EnrichItem.store_itementities(event, context)
            EnrichItem.store_itemphrases(event, context)

            event = {
                "pathParameters": {
                    "item_id": item.id
                }
            }
            context = {}
            s = time.perf_counter()
            response = get_online_factcheck.get_online_factcheck(event, context)
            elapsed = time.perf_counter() - s
            body = response['body']
            # Deserialize if body is string
            if isinstance(body, str):
                factcheck = json.loads(body)
            else:
                factcheck = body
            assert factcheck['url'] == 'https://dpa-factchecking.com/germany/201022-99-42791'
            assert factcheck['title'] == 'Vortrag über die PCR-Methode enthält mehrere falsche oder ...'
            assert elapsed < 3            


class TestStoreFactChecks:
    def test_store_factcheck_empty(self, database_fixture):

        with Session() as session:

            # creating items
            item = Item()
            item.content = "item is referencing some fact checks"
            item = item_handler.create_item(item, session)

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
            EnrichItem.store_factchecks(event, context)
            assert 1 == 1

class TestStoreTags:
    def test_store_itemtag(self, database_fixture):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            # creating items
            item = Item()
            item.content = "RKI bestätigt Covid-19 Sterblichkeitsrate von 0,01 Prozent in (...) - Corona Transition "
            item.language = "de"
            item = item_handler.create_item(item, session)
            list_tags = ['RKI', 'Covid', 'Corona Transition']

            # store tags
            event = {
                "item": item.to_dict(),
                "Tags": list_tags
            }
            context = ""
            EnrichItem.store_itemtags(event, context)

            tag = tag_handler.get_tag_by_content(list_tags[0], session)
            assert tag.tag == list_tags[0]

            itemtag = tag_handler.get_itemtag_by_tag_and_item_id(tag.id, item.id, session)
            assert itemtag.id is not None

            event = {
                "pathParameters": {
                    "item_id": item.id
                }
            }
            ret = GetTags.get_tags_for_item(event, context)
            body = ret['body']
            # Deserialize if body is string
            if isinstance(body, str):
                tags = json.loads(body)['Tags']
            else:
                tags = body['Tags']
            assert tags == list_tags
