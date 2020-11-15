import SearchFactChecks
import time


class TestSearchFactChecks:
    def test_search_checks_1(self):
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
        assert ret[0]['claimReview'][0]['title'] == 'Nein, RKI bestätigt nicht eine Covid-19-Sterblichkeitsrate ' \
                                                    'von 0,01 Prozent in Deutschland'
        assert elapsed < 3

class TestUpdateModels:
    def test_update_factchecker_1(self):
        event = ""
        context = ""
        SearchFactChecks.update_factcheck_models(event, context)
        df_factchecks = SearchFactChecks.read_df(SearchFactChecks.factchecks_prefix+"de.csv")
        assert "correctiv.org" in df_factchecks.values
        model_name = SearchFactChecks.doc2vec_models_prefix+"de"
        model = SearchFactChecks.read_model(model_name)
        vocab_len = len(model.wv.vocab)
        assert vocab_len > 0
