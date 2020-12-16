import time
import os
import SearchFactChecks
import UpdateFactChecks


class TestSearchFactChecks:
    def test_search_checks_1(self):
        os.environ["STAGE"] = "dev"
        event = {
            "item": {
                "id": "3fb83912-7a97-423a-b820-36718d51b1a6",
                "content": "https://corona-transition.org/rki-bestatigt-covid-19-sterblichkeitsrate-von-0-01"
                           "-prozent-in-deutschland?fbclid=IwAR2vLIkW_3EejFaeC5_wC_410uKhN_WMpWDMAcI"
                           "-dF9TTsZ43MwaHeSl4n8%22",
                "language": "de",
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
                "Deutschland",
                "RKI",
                "136 Kreisen",
                "Bundeskanzlerin"
            ],
            "TitleEntities": [
                "RKI",
                "0,01 Prozent",
                "19 Sterblichkeitsrate",
                "Corona Transition",
                "Covid"
            ],
            "Sentiment": "NEUTRAL"
        }
        context = ""
        s = time.perf_counter()
        ret = SearchFactChecks.get_FactChecks(event, context)
        elapsed = time.perf_counter() - s
        assert 'claimReview' in ret[0]
        assert ret[0]['claimReview'][0]['textualRating'] == 'Falsch. Das Robert-Koch-Institut bestätigte nicht eine Covid-19- Sterblichkeitsrate von 0,01 Prozent in Deutschland.'
        assert elapsed < 3

    def test_search_checks_2(self):
        os.environ["STAGE"] = "dev"
        event = {
            "item": {
                "id": "3fb83912-7a97-423a-b820-36718d51b1a6",
                "content": "Manche Corona-Tests brauchen keine externe Qualitätskontrolle",
                "language": "de"
            },
            "KeyPhrases": [
                "externe Qualitätskontrolle",
                "Corona-Tests"
            ],
            "Entities": [
            ],
            "TitleEntities": [
            ],
            "Sentiment": "NEUTRAL"
        }
        context = ""
        s = time.perf_counter()
        ret = SearchFactChecks.get_FactChecks(event, context)
        elapsed = time.perf_counter() - s
        assert 'claimReview' in ret[0]
        assert ret[0]['claimReview'][0]['title'] == 'Warum viele Corona-Tests noch keine Qualitätskontrolle brauchen'
        assert elapsed < 3

class TestUpdateModels:
    def test_update_factchecker_1(self):
        event = ""
        context = ""
        os.environ["STAGE"] = "dev"
        UpdateFactChecks.update_factcheck_models(event, context)
        df_factchecks = UpdateFactChecks.read_df(UpdateFactChecks.factchecks_prefix+"de.csv")
        fc_exists = False
        for fc in df_factchecks:
            if "correctiv.org" == fc['review_site']:
                fc_exists = True
                break
        assert fc_exists
